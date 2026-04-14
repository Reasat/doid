#!/usr/bin/env python3
"""
Serialize DOID component OWL → schema-conformant YAML.

Reads rdfs:label, obo:IAO_0000115, oboInOwl synonym properties, rdfs:subClassOf (named DOID
parents only), oboInOwl:hasDbXref, skos:*Match, skos:notation, and owl:deprecated.

OWL class restrictions (e.g. RO someValuesFrom) are not materialised as slots; is-a edges
to other DOID classes are.

Input:  tmp/transformed-doid.owl (ROBOT component output)
Output: doid.yaml  (conforms to linkml/mondo_source_schema.yaml)

Usage:
    python scripts/transform.py \\
        --input tmp/transformed-doid.owl \\
        --schema linkml/mondo_source_schema.yaml \\
        --output doid.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef
from rdflib.namespace import SKOS, Namespace

OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
DCES = Namespace("http://purl.org/dc/elements/1.1/")

DOID_IRI_PREFIX = "http://purl.obolibrary.org/obo/DOID_"
DOID_CURIE_PREFIX = "DOID:"

DEFINITION = OBO["IAO_0000115"]
OWL_DEPRECATED_PROP = OWL.deprecated


def is_doid_class_iri(iri: str) -> bool:
    if not iri.startswith(DOID_IRI_PREFIX):
        return False
    rest = iri[len(DOID_IRI_PREFIX) :]
    return rest.isdigit()


def iri_to_curie(iri: str) -> str:
    return DOID_CURIE_PREFIX + iri[len(DOID_IRI_PREFIX) :]


def _literal_values(g: Graph, subj: URIRef, pred) -> list[str]:
    out = [str(o) for o in g.objects(subj, pred) if isinstance(o, Literal)]
    return sorted(set(out)) if out else []


def _uri_or_literal_values(g: Graph, subj: URIRef, pred) -> list[str]:
    out: list[str] = []
    for o in g.objects(subj, pred):
        if isinstance(o, (Literal, URIRef)):
            val = str(o).strip()
            if val:
                out.append(val)
    return sorted(set(out)) if out else []


def get_direct_doid_parents(g: Graph, subj: URIRef) -> list[str]:
    parents: list[str] = []
    for o in g.objects(subj, RDFS.subClassOf):
        if not isinstance(o, URIRef):
            continue
        oiri = str(o)
        if oiri == str(OWL.Thing):
            continue
        if is_doid_class_iri(oiri):
            parents.append(iri_to_curie(oiri))
    return sorted(parents)


def extract_ontology_document(g: Graph) -> dict:
    doc: dict = {}
    for ont in g.subjects(RDF.type, OWL.Ontology):
        if not isinstance(ont, URIRef):
            continue
        t = g.value(ont, DCES.title)
        lbl = g.value(ont, RDFS.label)
        if t:
            doc["title"] = str(t)
        elif lbl:
            doc["title"] = str(lbl)
        ver = g.value(ont, OWL.versionInfo)
        if ver:
            doc["version"] = str(ver)
        break

    if "title" not in doc:
        doc["title"] = "Human Disease Ontology"
    if "version" not in doc:
        doc["version"] = "unknown"
    return doc


def extract_terms(g: Graph) -> list[dict]:
    candidate_iris: set[str] = {
        str(s)
        for s in g.subjects(RDF.type, OWL.Class)
        if isinstance(s, URIRef) and is_doid_class_iri(str(s))
    }

    terms: list[dict] = []

    for iri in sorted(candidate_iris):
        subj = URIRef(iri)
        curie = iri_to_curie(iri)

        label_node = g.value(subj, RDFS.label)
        if label_node is None:
            continue
        label = str(label_node)

        dep_node = g.value(subj, OWL_DEPRECATED_PROP)
        is_deprecated = dep_node is not None and str(dep_node).strip().lower() == "true"

        defn_node = g.value(subj, DEFINITION)
        definition = str(defn_node) if defn_node else None

        exact_syns: list[str] = [
            str(o) for o in g.objects(subj, OBOINOWL.hasExactSynonym) if isinstance(o, Literal)
        ]

        parent_curies = get_direct_doid_parents(g, subj)

        has_thing_parent = OWL.Thing in g.objects(subj, RDFS.subClassOf)
        is_root = has_thing_parent or len(parent_curies) == 0

        term: dict = {"id": curie, "label": label}
        if is_deprecated:
            term["deprecated"] = True
        if definition:
            term["definition"] = definition
        if exact_syns:
            term["exact_synonyms"] = [{"synonym_text": s} for s in sorted(set(exact_syns))]
        if not is_root:
            term["parents"] = parent_curies

        for key, pred in (
            ("related_synonyms", OBOINOWL.hasRelatedSynonym),
            ("narrow_synonyms", OBOINOWL.hasNarrowSynonym),
            ("broad_synonyms", OBOINOWL.hasBroadSynonym),
        ):
            vals = _literal_values(g, subj, pred)
            if vals:
                term[key] = [{"synonym_text": s} for s in vals]

        xrefs = _uri_or_literal_values(g, subj, OBOINOWL.hasDbXref)
        notations = _uri_or_literal_values(g, subj, SKOS.notation)
        all_xrefs = sorted(set(xrefs + notations))

        for key, pred in (
            ("skos_exact_match", SKOS.exactMatch),
            ("skos_broad_match", SKOS.broadMatch),
            ("skos_narrow_match", SKOS.narrowMatch),
            ("skos_related_match", SKOS.relatedMatch),
        ):
            vals = _uri_or_literal_values(g, subj, pred)
            if vals:
                term[key] = vals

        if all_xrefs:
            existing = term.get("skos_exact_match", [])
            term["skos_exact_match"] = sorted(set(existing + all_xrefs))

        terms.append(term)

    return terms


def transform(input_path: Path, output_path: Path) -> None:
    print(f"Parsing component OWL: {input_path}", file=sys.stderr)
    g = Graph()
    g.parse(str(input_path))

    doc = extract_ontology_document(g)
    terms = extract_terms(g)

    active = sum(1 for t in terms if not t.get("deprecated"))
    deprecated = sum(1 for t in terms if t.get("deprecated"))
    print(
        f"Extracted {len(terms)} DOID terms ({active} active, {deprecated} deprecated)",
        file=sys.stderr,
    )

    doc["terms"] = terms

    class QuotedDumper(yaml.Dumper):
        pass

    QuotedDumper.add_representer(
        str,
        lambda dumper, data: dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
        if any(c in data for c in ",:{}")
        else dumper.represent_scalar("tag:yaml.org,2002:str", data),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.dump(
            doc,
            fh,
            Dumper=QuotedDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    print(f"Written: {output_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serialize DOID component OWL → schema YAML")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    if not args.schema.exists():
        print(f"Error: schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    transform(args.input, args.output)


if __name__ == "__main__":
    main()

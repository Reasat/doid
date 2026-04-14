from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.7.0"
version = "0.4.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'mondo_src',
     'default_range': 'string',
     'description': 'LinkML schema for a Mondo-ready ontology source (DOID '
                    'ingest). Core fields: labels, definitions, synonyms, '
                    'hierarchy. Extended slots align with predicates allowed to '
                    'remain on component OWL after ROBOT preprocessing (see '
                    'config/properties.txt); populate only what the transform '
                    'exports.',
     'id': 'https://w3id.org/monarch-initiative/mondo-source-schema',
     'imports': ['linkml:types'],
     'name': 'mondo_source_schema',
     'prefixes': {'BFO': {'prefix_prefix': 'BFO',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/BFO_'},
                  'DOID': {'prefix_prefix': 'DOID',
                           'prefix_reference': 'http://purl.obolibrary.org/obo/DOID_'},
                  'MONDO': {'prefix_prefix': 'MONDO',
                            'prefix_reference': 'http://purl.obolibrary.org/obo/mondo#'},
                  'RO': {'prefix_prefix': 'RO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/RO_'},
                  'dcterms': {'prefix_prefix': 'dcterms',
                              'prefix_reference': 'http://purl.org/dc/terms/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'mondo_src': {'prefix_prefix': 'mondo_src',
                                'prefix_reference': 'https://w3id.org/monarch-initiative/mondo-source-schema/'},
                  'obo': {'prefix_prefix': 'obo',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/'},
                  'oboInOwl': {'prefix_prefix': 'oboInOwl',
                               'prefix_reference': 'http://www.geneontology.org/formats/oboInOwl#'},
                  'owl': {'prefix_prefix': 'owl',
                          'prefix_reference': 'http://www.w3.org/2002/07/owl#'},
                  'rdfs': {'prefix_prefix': 'rdfs',
                           'prefix_reference': 'http://www.w3.org/2000/01/rdf-schema#'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'}},
     'source_file': 'linkml/mondo_source_schema.yaml'} )

class SynonymTypeEnum(str, Enum):
    """
    Types of synonyms used in Mondo source ingests.
    """
    omim_included = "omim_included"
    """
    Synonym from an included OMIM entry.
    """
    generated_from_label = "generated_from_label"
    """
    Synonym automatically generated from the label.
    """
    generated = "generated"
    """
    Automatically generated synonym.
    """
    omim_formerly = "omim_formerly"
    """
    Synonym from a formerly associated OMIM entry.
    """
    abbreviation = "abbreviation"
    """
    Abbreviation synonym.
    """



class OntologyDocument(ConfiguredBaseModel):
    """
    Top-level container representing a single ontology source release.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'owl:Ontology',
         'from_schema': 'https://w3id.org/monarch-initiative/mondo-source-schema',
         'tree_root': True})

    title: str = Field(default=..., description="""Primary human-readable name of the ontology (maps to rdfs:label on owl:Ontology, matching BioPortal / component OWL).""", json_schema_extra = { "linkml_meta": {'domain_of': ['OntologyDocument'], 'slot_uri': 'rdfs:label'} })
    dcterms_title: Optional[str] = Field(default=None, description="""Optional Dublin Core title (dcterms:title) when present on the ontology.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyDocument'],
         'slot_uri': 'dcterms:title'} })
    version: str = Field(default=..., description="""Version string for this release (e.g. \"2024ab\" or \"2025-03-01\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['OntologyDocument'], 'slot_uri': 'owl:versionInfo'} })
    sources: Optional[list[str]] = Field(default=None, description="""oboInOwl:source.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyDocument', 'OntologyTerm'],
         'slot_uri': 'oboInOwl:source'} })
    terms: list[OntologyTerm] = Field(default=..., description="""All terms included in this source release.""", json_schema_extra = { "linkml_meta": {'domain_of': ['OntologyDocument']} })


class Synonym(ConfiguredBaseModel):
    """
    A synonym value with an optional type annotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/monarch-initiative/mondo-source-schema'})

    synonym_text: str = Field(default=..., description="""The synonym string value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Synonym']} })
    synonym_type: Optional[SynonymTypeEnum] = Field(default=None, description="""Optional type annotation for this synonym.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Synonym']} })


class OntologyTerm(ConfiguredBaseModel):
    """
    A single class / concept from the source ontology.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'owl:Class',
         'from_schema': 'https://w3id.org/monarch-initiative/mondo-source-schema',
         'slot_usage': {'broad_synonyms': {'annotations': {'owl.template': {'tag': 'owl.template',
                                                                            'value': '{% '
                                                                                     'for '
                                                                                     's '
                                                                                     'in '
                                                                                     'broad_synonyms '
                                                                                     '%}\n'
                                                                                     'AnnotationAssertion({% '
                                                                                     'if '
                                                                                     's.synonym_type '
                                                                                     '%}Annotation(oboInOwl:hasSynonymType '
                                                                                     '{{s.synonym_type.meaning}}) '
                                                                                     '{% '
                                                                                     'endif '
                                                                                     '%}oboInOwl:hasBroadSynonym '
                                                                                     '{{id}} '
                                                                                     '"{{s.synonym_text|replace(\'"\', '
                                                                                     '\'\\\\"\')}}")\n'
                                                                                     '{% '
                                                                                     'endfor '
                                                                                     '%}'}},
                                           'name': 'broad_synonyms'},
                        'exact_synonyms': {'annotations': {'owl.template': {'tag': 'owl.template',
                                                                            'value': '{% '
                                                                                     'for '
                                                                                     's '
                                                                                     'in '
                                                                                     'exact_synonyms '
                                                                                     '%}\n'
                                                                                     'AnnotationAssertion({% '
                                                                                     'if '
                                                                                     's.synonym_type '
                                                                                     '%}Annotation(oboInOwl:hasSynonymType '
                                                                                     '{{s.synonym_type.meaning}}) '
                                                                                     '{% '
                                                                                     'endif '
                                                                                     '%}oboInOwl:hasExactSynonym '
                                                                                     '{{id}} '
                                                                                     '"{{s.synonym_text|replace(\'"\', '
                                                                                     '\'\\\\"\')}}")\n'
                                                                                     '{% '
                                                                                     'endfor '
                                                                                     '%}'}},
                                           'name': 'exact_synonyms'},
                        'narrow_synonyms': {'annotations': {'owl.template': {'tag': 'owl.template',
                                                                             'value': '{% '
                                                                                      'for '
                                                                                      's '
                                                                                      'in '
                                                                                      'narrow_synonyms '
                                                                                      '%}\n'
                                                                                      'AnnotationAssertion({% '
                                                                                      'if '
                                                                                      's.synonym_type '
                                                                                      '%}Annotation(oboInOwl:hasSynonymType '
                                                                                      '{{s.synonym_type.meaning}}) '
                                                                                      '{% '
                                                                                      'endif '
                                                                                      '%}oboInOwl:hasNarrowSynonym '
                                                                                      '{{id}} '
                                                                                      '"{{s.synonym_text|replace(\'"\', '
                                                                                      '\'\\\\"\')}}")\n'
                                                                                      '{% '
                                                                                      'endfor '
                                                                                      '%}'}},
                                            'name': 'narrow_synonyms'},
                        'related_synonyms': {'annotations': {'owl.template': {'tag': 'owl.template',
                                                                              'value': '{% '
                                                                                       'for '
                                                                                       's '
                                                                                       'in '
                                                                                       'related_synonyms '
                                                                                       '%}\n'
                                                                                       'AnnotationAssertion({% '
                                                                                       'if '
                                                                                       's.synonym_type '
                                                                                       '%}Annotation(oboInOwl:hasSynonymType '
                                                                                       '{{s.synonym_type.meaning}}) '
                                                                                       '{% '
                                                                                       'endif '
                                                                                       '%}oboInOwl:hasRelatedSynonym '
                                                                                       '{{id}} '
                                                                                       '"{{s.synonym_text|replace(\'"\', '
                                                                                       '\'\\\\"\')}}")\n'
                                                                                       '{% '
                                                                                       'endfor '
                                                                                       '%}'}},
                                             'name': 'related_synonyms'}}})

    id: str = Field(default=..., description="""Canonical CURIE identifier for the term (e.g. \"ICD10CM:A00\" or \"ICD10WHO:A00\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['OntologyTerm'], 'slot_uri': 'dcterms:identifier'} })
    label: str = Field(default=..., description="""The preferred human-readable label.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'rdfs:label'} })
    definition: Optional[str] = Field(default=None, description="""Textual definition (IAO:0000115).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'recommended': True,
         'slot_uri': 'obo:IAO_0000115'} })
    exact_synonyms: Optional[list[Synonym]] = Field(default=None, description="""Exact-match synonyms (oboInOwl:hasExactSynonym).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl.template': {'tag': 'owl.template',
                                          'value': '{% for s in exact_synonyms %}\n'
                                                   'AnnotationAssertion({% if '
                                                   's.synonym_type '
                                                   '%}Annotation(oboInOwl:hasSynonymType '
                                                   '{{s.synonym_type.meaning}}) {% '
                                                   'endif %}oboInOwl:hasExactSynonym '
                                                   '{{id}} '
                                                   '"{{s.synonym_text|replace(\'"\', '
                                                   '\'\\\\"\')}}")\n'
                                                   '{% endfor %}'}},
         'domain_of': ['OntologyTerm'],
         'recommended': True,
         'slot_uri': 'oboInOwl:hasExactSynonym'} })
    related_synonyms: Optional[list[Synonym]] = Field(default=None, description="""Related synonyms (oboInOwl:hasRelatedSynonym).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl.template': {'tag': 'owl.template',
                                          'value': '{% for s in related_synonyms %}\n'
                                                   'AnnotationAssertion({% if '
                                                   's.synonym_type '
                                                   '%}Annotation(oboInOwl:hasSynonymType '
                                                   '{{s.synonym_type.meaning}}) {% '
                                                   'endif %}oboInOwl:hasRelatedSynonym '
                                                   '{{id}} '
                                                   '"{{s.synonym_text|replace(\'"\', '
                                                   '\'\\\\"\')}}")\n'
                                                   '{% endfor %}'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'oboInOwl:hasRelatedSynonym'} })
    narrow_synonyms: Optional[list[Synonym]] = Field(default=None, description="""Narrower synonyms (oboInOwl:hasNarrowSynonym).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl.template': {'tag': 'owl.template',
                                          'value': '{% for s in narrow_synonyms %}\n'
                                                   'AnnotationAssertion({% if '
                                                   's.synonym_type '
                                                   '%}Annotation(oboInOwl:hasSynonymType '
                                                   '{{s.synonym_type.meaning}}) {% '
                                                   'endif %}oboInOwl:hasNarrowSynonym '
                                                   '{{id}} '
                                                   '"{{s.synonym_text|replace(\'"\', '
                                                   '\'\\\\"\')}}")\n'
                                                   '{% endfor %}'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'oboInOwl:hasNarrowSynonym'} })
    broad_synonyms: Optional[list[Synonym]] = Field(default=None, description="""Broader synonyms (oboInOwl:hasBroadSynonym).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl.template': {'tag': 'owl.template',
                                          'value': '{% for s in broad_synonyms %}\n'
                                                   'AnnotationAssertion({% if '
                                                   's.synonym_type '
                                                   '%}Annotation(oboInOwl:hasSynonymType '
                                                   '{{s.synonym_type.meaning}}) {% '
                                                   'endif %}oboInOwl:hasBroadSynonym '
                                                   '{{id}} '
                                                   '"{{s.synonym_text|replace(\'"\', '
                                                   '\'\\\\"\')}}")\n'
                                                   '{% endfor %}'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'oboInOwl:hasBroadSynonym'} })
    close_synonyms: Optional[list[str]] = Field(default=None, description="""skos:closeMatch (mapping / close match).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'skos:closeMatch'} })
    in_subsets: Optional[list[str]] = Field(default=None, description="""oboInOwl:inSubset.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'oboInOwl:inSubset'} })
    sources: Optional[list[str]] = Field(default=None, description="""oboInOwl:source.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyDocument', 'OntologyTerm'],
         'slot_uri': 'oboInOwl:source'} })
    synonym_types: Optional[list[str]] = Field(default=None, description="""oboInOwl:hasSynonymType.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'oboInOwl:hasSynonymType'} })
    skos_exact_match: Optional[list[str]] = Field(default=None, description="""skos:exactMatch.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'skos:exactMatch'} })
    skos_broad_match: Optional[list[str]] = Field(default=None, description="""skos:broadMatch.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'skos:broadMatch'} })
    skos_narrow_match: Optional[list[str]] = Field(default=None, description="""skos:narrowMatch.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'skos:narrowMatch'} })
    skos_related_match: Optional[list[str]] = Field(default=None, description="""skos:relatedMatch.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'skos:relatedMatch'} })
    omo_0003012: Optional[list[str]] = Field(default=None, description="""OMO:0003012 (ontology metadata slot used on some terms).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'obo:OMO_0003012'} })
    has_material_basis_in_germline_mutation_in: Optional[list[str]] = Field(default=None, description="""Germline mutation causal basis (RO:0004001).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'ObjectSomeValuesFrom'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'RO:0004001'} })
    has_material_basis_in_somatic_mutation_in: Optional[list[str]] = Field(default=None, description="""Somatic mutation causal basis (RO:0004003).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'ObjectSomeValuesFrom'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'RO:0004003'} })
    has_material_basis_in: Optional[list[str]] = Field(default=None, description="""General material basis (RO:0004004).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'ObjectSomeValuesFrom'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'RO:0004004'} })
    part_of: Optional[list[str]] = Field(default=None, description="""Part-of relationship (BFO:0000050).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'ObjectSomeValuesFrom'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'BFO:0000050'} })
    has_part: Optional[list[str]] = Field(default=None, description="""Has-part relationship (BFO:0000051).""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'ObjectSomeValuesFrom'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'BFO:0000051'} })
    parents: Optional[list[str]] = Field(default=None, description="""Direct is-a parents (source CURIEs). Non-source subclass targets are not listed.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'SubClassOf'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'rdfs:subClassOf'} })
    deprecated: Optional[bool] = Field(default=None, description="""True when this term is marked owl:deprecated.""", json_schema_extra = { "linkml_meta": {'annotations': {'owl': {'tag': 'owl', 'value': 'AnnotationAssertion'}},
         'domain_of': ['OntologyTerm'],
         'slot_uri': 'owl:deprecated'} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
OntologyDocument.model_rebuild()
Synonym.model_rebuild()
OntologyTerm.model_rebuild()

# DOID — Disease Ontology source-specific rules.

DOID_URL ?= http://purl.obolibrary.org/obo/doid.owl

ifeq ($(MIR),true)
$(RAW_OWL): | $(TMP_DIR)
	wget $(DOID_URL) -O $@
	@echo "Downloaded: $@"
endif

# ROBOT component: remove imports, normalize xref strings, property allowlist, ontology IRIs
$(OUTPUT_OWL): $(MIRROR_OWL) \
		$(CONFIG_DIR)/properties.txt \
		$(SPARQL_DIR)/fix_xref_prefixes.ru
	$(ROBOT) remove -i $(MIRROR_OWL) --select imports \
		query \
			--update $(SPARQL_DIR)/fix_xref_prefixes.ru \
		remove -T $(CONFIG_DIR)/properties.txt --select complement --select properties --trim true \
		annotate \
			--ontology-iri $(URIBASE)/mondo/sources/$(SOURCE).owl \
			--version-iri $(URIBASE)/mondo/sources/$(TODAY)/$(SOURCE).owl \
		-o $@
	@echo "Build complete: $@"

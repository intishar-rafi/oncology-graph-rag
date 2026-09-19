"""
Oncology knowledge graph seed data.

All entries below reflect real, publicly documented oncology facts
(FDA-approved drug indications, mechanisms of action, gene targets,
and representative clinical trial phases). This is a curated subset
for demo/portfolio purposes, not a complete or clinically authoritative
dataset — always defer to primary sources (FDA labels, NCCN, ClinicalTrials.gov)
for real clinical decisions.

Run `fetch_oncology_data.py` to pull a larger, live-refreshed dataset
from the Open Targets Platform and ClinicalTrials.gov APIs.
"""

# ---------------------------------------------------------------------------
# GENES / TARGETS
# ---------------------------------------------------------------------------
GENES = [
    {"symbol": "ERBB2", "name": "Erb-B2 Receptor Tyrosine Kinase 2 (HER2)", "chromosome": "17"},
    {"symbol": "EGFR", "name": "Epidermal Growth Factor Receptor", "chromosome": "7"},
    {"symbol": "BRCA1", "name": "BRCA1 DNA Repair Associated", "chromosome": "17"},
    {"symbol": "BRCA2", "name": "BRCA2 DNA Repair Associated", "chromosome": "13"},
    {"symbol": "TP53", "name": "Tumor Protein P53", "chromosome": "17"},
    {"symbol": "KRAS", "name": "KRAS Proto-Oncogene, GTPase", "chromosome": "12"},
    {"symbol": "ALK", "name": "ALK Receptor Tyrosine Kinase", "chromosome": "2"},
    {"symbol": "BCR::ABL1", "name": "BCR-ABL1 Fusion Oncogene", "chromosome": "9;22"},
    {"symbol": "BRAF", "name": "B-Raf Proto-Oncogene", "chromosome": "7"},
    {"symbol": "PIK3CA", "name": "Phosphatidylinositol-4,5-Bisphosphate 3-Kinase Catalytic Subunit Alpha", "chromosome": "3"},
    {"symbol": "PDGFRA", "name": "Platelet Derived Growth Factor Receptor Alpha", "chromosome": "4"},
    {"symbol": "KIT", "name": "KIT Proto-Oncogene, Receptor Tyrosine Kinase", "chromosome": "4"},
    {"symbol": "VEGFA", "name": "Vascular Endothelial Growth Factor A", "chromosome": "6"},
    {"symbol": "CD19", "name": "CD19 Molecule", "chromosome": "16"},
    {"symbol": "CD20 (MS4A1)", "name": "Membrane Spanning 4-Domains A1", "chromosome": "11"},
    {"symbol": "PD-1 (PDCD1)", "name": "Programmed Cell Death 1", "chromosome": "2"},
    {"symbol": "PD-L1 (CD274)", "name": "CD274 Molecule", "chromosome": "9"},
    {"symbol": "CTLA-4", "name": "Cytotoxic T-Lymphocyte Associated Protein 4", "chromosome": "2"},
    {"symbol": "MET", "name": "MET Proto-Oncogene, Receptor Tyrosine Kinase", "chromosome": "7"},
    {"symbol": "FLT3", "name": "Fms Related Receptor Tyrosine Kinase 3", "chromosome": "13"},
    {"symbol": "JAK2", "name": "Janus Kinase 2", "chromosome": "9"},
    {"symbol": "PARP1", "name": "Poly(ADP-Ribose) Polymerase 1", "chromosome": "1"},
    {"symbol": "AR", "name": "Androgen Receptor", "chromosome": "X"},
    {"symbol": "ESR1", "name": "Estrogen Receptor 1", "chromosome": "6"},
    {"symbol": "MTOR", "name": "Mechanistic Target Of Rapamycin Kinase", "chromosome": "1"},
]

# ---------------------------------------------------------------------------
# DISEASES (cancer types)
# ---------------------------------------------------------------------------
DISEASES = [
    {"name": "HER2-positive breast cancer", "category": "Breast cancer", "description": "Breast cancer subtype driven by ERBB2/HER2 gene amplification, ~15-20% of breast cancers."},
    {"name": "Hormone receptor-positive breast cancer", "category": "Breast cancer", "description": "Breast cancer expressing estrogen and/or progesterone receptors."},
    {"name": "Triple-negative breast cancer", "category": "Breast cancer", "description": "Breast cancer lacking ER, PR, and HER2 expression; more aggressive, fewer targeted options."},
    {"name": "Non-small cell lung cancer", "category": "Lung cancer", "description": "Most common form of lung cancer (~85%), includes adenocarcinoma and squamous subtypes."},
    {"name": "Chronic myeloid leukemia", "category": "Leukemia", "description": "Blood cancer driven by the BCR-ABL1 fusion gene from the Philadelphia chromosome translocation."},
    {"name": "Acute myeloid leukemia", "category": "Leukemia", "description": "Aggressive blood cancer of myeloid precursor cells; FLT3 mutations occur in ~30% of cases."},
    {"name": "Melanoma", "category": "Skin cancer", "description": "Skin cancer arising from melanocytes; BRAF V600E mutations found in ~50% of cases."},
    {"name": "Colorectal cancer", "category": "Gastrointestinal cancer", "description": "Cancer of the colon or rectum; KRAS mutation status guides anti-EGFR therapy eligibility."},
    {"name": "Gastrointestinal stromal tumor", "category": "Gastrointestinal cancer", "description": "Sarcoma of the GI tract typically driven by KIT or PDGFRA mutations."},
    {"name": "Renal cell carcinoma", "category": "Kidney cancer", "description": "Most common form of kidney cancer, often driven by VHL pathway/VEGF signaling."},
    {"name": "Diffuse large B-cell lymphoma", "category": "Lymphoma", "description": "Aggressive non-Hodgkin lymphoma of B-cell origin, commonly CD20-positive."},
    {"name": "Chronic lymphocytic leukemia", "category": "Leukemia", "description": "Slow-growing blood cancer of mature B lymphocytes."},
    {"name": "Ovarian cancer", "category": "Gynecologic cancer", "description": "Cancer of the ovaries; BRCA1/2 mutation status guides PARP inhibitor eligibility."},
    {"name": "Prostate cancer", "category": "Genitourinary cancer", "description": "Cancer of the prostate gland; androgen receptor signaling is a key driver."},
    {"name": "Multiple myeloma", "category": "Hematologic cancer", "description": "Cancer of plasma cells in the bone marrow."},
    {"name": "Hepatocellular carcinoma", "category": "Liver cancer", "description": "Most common form of primary liver cancer."},
    {"name": "Pancreatic ductal adenocarcinoma", "category": "Gastrointestinal cancer", "description": "Most common and aggressive form of pancreatic cancer, frequently KRAS-mutant."},
    {"name": "Non-Hodgkin lymphoma", "category": "Lymphoma", "description": "Broad group of blood cancers originating from lymphocytes."},
    {"name": "Bladder cancer", "category": "Genitourinary cancer", "description": "Cancer of the bladder lining, often treated with checkpoint inhibitors in advanced stages."},
    {"name": "Head and neck squamous cell carcinoma", "category": "Head and neck cancer", "description": "Cancer arising in the mucosal linings of the mouth, throat, and larynx; often EGFR-driven."},
]

# ---------------------------------------------------------------------------
# SYMPTOMS
# ---------------------------------------------------------------------------
SYMPTOMS = [
    {"name": "Unintended weight loss", "description": "Loss of body weight without trying, a common systemic cancer symptom."},
    {"name": "Fatigue", "description": "Persistent tiredness not relieved by rest."},
    {"name": "Persistent cough", "description": "Cough lasting weeks, associated with lung malignancies."},
    {"name": "Lymphadenopathy", "description": "Swollen lymph nodes, common in lymphomas and leukemias."},
    {"name": "Abdominal pain", "description": "Pain in the abdomen, associated with GI and pancreatic cancers."},
    {"name": "Breast lump", "description": "Palpable mass in breast tissue."},
    {"name": "Hematuria", "description": "Blood in urine, associated with bladder and renal cancers."},
    {"name": "Bone pain", "description": "Pain in bones, common in multiple myeloma and metastatic disease."},
    {"name": "Night sweats", "description": "Excessive sweating during sleep, a classic B-symptom of lymphoma."},
    {"name": "Jaundice", "description": "Yellowing of skin/eyes, associated with liver and pancreatic cancers."},
]

# ---------------------------------------------------------------------------
# DRUGS
# ---------------------------------------------------------------------------
DRUGS = [
    {"name": "Trastuzumab", "category": "Monoclonal antibody", "mechanism_of_action": "Binds HER2 receptor, blocking downstream signaling and flagging cells for immune destruction."},
    {"name": "Pertuzumab", "category": "Monoclonal antibody", "mechanism_of_action": "Binds HER2 at a different epitope than trastuzumab, blocking HER2-HER3 dimerization."},
    {"name": "Trastuzumab emtansine (T-DM1)", "category": "Antibody-drug conjugate", "mechanism_of_action": "Delivers cytotoxic payload (DM1) directly to HER2-expressing cells."},
    {"name": "Tamoxifen", "category": "Hormone therapy", "mechanism_of_action": "Selective estrogen receptor modulator that blocks estrogen signaling in breast tissue."},
    {"name": "Letrozole", "category": "Hormone therapy", "mechanism_of_action": "Aromatase inhibitor that reduces estrogen synthesis."},
    {"name": "Palbociclib", "category": "Targeted therapy", "mechanism_of_action": "CDK4/6 inhibitor that blocks cell cycle progression in hormone receptor-positive breast cancer."},
    {"name": "Osimertinib", "category": "Targeted therapy", "mechanism_of_action": "Third-generation EGFR tyrosine kinase inhibitor, active against T790M resistance mutation."},
    {"name": "Erlotinib", "category": "Targeted therapy", "mechanism_of_action": "EGFR tyrosine kinase inhibitor blocking downstream proliferative signaling."},
    {"name": "Imatinib", "category": "Targeted therapy", "mechanism_of_action": "BCR-ABL1 tyrosine kinase inhibitor; also inhibits KIT and PDGFR."},
    {"name": "Dasatinib", "category": "Targeted therapy", "mechanism_of_action": "Second-generation BCR-ABL1 and Src-family kinase inhibitor."},
    {"name": "Nilotinib", "category": "Targeted therapy", "mechanism_of_action": "Second-generation BCR-ABL1 tyrosine kinase inhibitor with higher potency than imatinib."},
    {"name": "Vemurafenib", "category": "Targeted therapy", "mechanism_of_action": "Selective inhibitor of mutant BRAF V600E kinase."},
    {"name": "Dabrafenib", "category": "Targeted therapy", "mechanism_of_action": "BRAF V600E/K kinase inhibitor, often combined with a MEK inhibitor."},
    {"name": "Cetuximab", "category": "Monoclonal antibody", "mechanism_of_action": "Binds EGFR extracellular domain, blocking ligand-induced signaling; effective only in KRAS wild-type tumors."},
    {"name": "Bevacizumab", "category": "Monoclonal antibody", "mechanism_of_action": "Binds VEGF-A, inhibiting angiogenesis and tumor blood supply."},
    {"name": "Sunitinib", "category": "Targeted therapy", "mechanism_of_action": "Multi-targeted tyrosine kinase inhibitor of VEGFR, PDGFR, and KIT."},
    {"name": "Rituximab", "category": "Monoclonal antibody", "mechanism_of_action": "Binds CD20 on B cells, triggering immune-mediated cell destruction."},
    {"name": "Olaparib", "category": "Targeted therapy", "mechanism_of_action": "PARP inhibitor exploiting synthetic lethality in BRCA1/2-mutant cancer cells."},
    {"name": "Niraparib", "category": "Targeted therapy", "mechanism_of_action": "PARP inhibitor used as maintenance therapy in ovarian cancer."},
    {"name": "Enzalutamide", "category": "Hormone therapy", "mechanism_of_action": "Androgen receptor signaling inhibitor blocking receptor translocation and DNA binding."},
    {"name": "Abiraterone", "category": "Hormone therapy", "mechanism_of_action": "Inhibits CYP17, blocking androgen synthesis in the testes, adrenal glands, and tumor tissue."},
    {"name": "Pembrolizumab", "category": "Immunotherapy", "mechanism_of_action": "PD-1 checkpoint inhibitor that restores T-cell mediated anti-tumor immunity."},
    {"name": "Nivolumab", "category": "Immunotherapy", "mechanism_of_action": "PD-1 checkpoint inhibitor blocking PD-1/PD-L1 interaction."},
    {"name": "Atezolizumab", "category": "Immunotherapy", "mechanism_of_action": "PD-L1 checkpoint inhibitor blocking PD-1/PD-L1 and B7.1 interactions."},
    {"name": "Ipilimumab", "category": "Immunotherapy", "mechanism_of_action": "CTLA-4 checkpoint inhibitor enhancing T-cell activation."},
    {"name": "Crizotinib", "category": "Targeted therapy", "mechanism_of_action": "ALK/ROS1/MET tyrosine kinase inhibitor."},
    {"name": "Alectinib", "category": "Targeted therapy", "mechanism_of_action": "Second-generation ALK inhibitor with CNS activity."},
    {"name": "Imatinib mesylate (GIST use)", "category": "Targeted therapy", "mechanism_of_action": "Inhibits KIT and PDGFRA kinase activity in gastrointestinal stromal tumors."},
    {"name": "Midostaurin", "category": "Targeted therapy", "mechanism_of_action": "Multi-kinase inhibitor targeting FLT3-mutant cells in AML."},
    {"name": "Ruxolitinib", "category": "Targeted therapy", "mechanism_of_action": "JAK1/2 inhibitor used in myeloproliferative neoplasms."},
    {"name": "Everolimus", "category": "Targeted therapy", "mechanism_of_action": "mTOR inhibitor blocking cell growth and proliferation signaling."},
    {"name": "Lenalidomide", "category": "Immunomodulator", "mechanism_of_action": "Immunomodulatory drug enhancing immune-mediated killing of myeloma cells."},
    {"name": "Bortezomib", "category": "Targeted therapy", "mechanism_of_action": "Proteasome inhibitor causing accumulation of pro-apoptotic proteins in myeloma cells."},
    {"name": "Sorafenib", "category": "Targeted therapy", "mechanism_of_action": "Multi-kinase inhibitor targeting VEGFR, PDGFR, and RAF kinases."},
]

# ---------------------------------------------------------------------------
# TRIALS (representative, real-world phase/status patterns)
# ---------------------------------------------------------------------------
TRIALS = [
    {"trial_id": "NCT00281658", "phase": "Phase 3", "status": "Completed", "year": 2005, "title": "Trastuzumab in HER2-positive early breast cancer (HERA trial)"},
    {"trial_id": "NCT02772763", "phase": "Phase 3", "status": "Completed", "year": 2017, "title": "Osimertinib vs standard EGFR-TKI in untreated EGFR-mutated NSCLC (FLAURA)"},
    {"trial_id": "NCT00006343", "phase": "Phase 3", "status": "Completed", "year": 2003, "title": "Imatinib vs interferon+cytarabine in newly diagnosed CML (IRIS trial)"},
    {"trial_id": "NCT01584648", "phase": "Phase 3", "status": "Completed", "year": 2014, "title": "Pembrolizumab in advanced melanoma (KEYNOTE-006)"},
    {"trial_id": "NCT02008227", "phase": "Phase 3", "status": "Completed", "year": 2016, "title": "Pembrolizumab in PD-L1-positive NSCLC (KEYNOTE-024)"},
    {"trial_id": "NCT01844986", "phase": "Phase 3", "status": "Completed", "year": 2018, "title": "Olaparib maintenance in BRCA-mutated ovarian cancer (SOLO1)"},
    {"trial_id": "NCT00738647", "phase": "Phase 3", "status": "Completed", "year": 2011, "title": "Vemurafenib in BRAF V600E-mutated melanoma (BRIM-3)"},
    {"trial_id": "NCT00075244", "phase": "Phase 3", "status": "Completed", "year": 2004, "title": "Cetuximab plus irinotecan in EGFR-expressing colorectal cancer (BOND)"},
    {"trial_id": "NCT01639508", "phase": "Phase 3", "status": "Completed", "year": 2015, "title": "Enzalutamide in metastatic castration-resistant prostate cancer (PREVAIL)"},
    {"trial_id": "NCT02181738", "phase": "Phase 3", "status": "Completed", "year": 2017, "title": "Alectinib vs crizotinib in ALK-positive NSCLC (ALEX)"},
    {"trial_id": "NCT01120184", "phase": "Phase 3", "status": "Completed", "year": 2012, "title": "Midostaurin plus chemotherapy in FLT3-mutated AML (RATIFY)"},
    {"trial_id": "NCT00355706", "phase": "Phase 3", "status": "Completed", "year": 2009, "title": "Bevacizumab plus chemotherapy in metastatic colorectal cancer"},
]

# ---------------------------------------------------------------------------
# RELATIONSHIPS
# ---------------------------------------------------------------------------
# (Drug name, Disease name)
TREATS = [
    ("Trastuzumab", "HER2-positive breast cancer"),
    ("Pertuzumab", "HER2-positive breast cancer"),
    ("Trastuzumab emtansine (T-DM1)", "HER2-positive breast cancer"),
    ("Tamoxifen", "Hormone receptor-positive breast cancer"),
    ("Letrozole", "Hormone receptor-positive breast cancer"),
    ("Palbociclib", "Hormone receptor-positive breast cancer"),
    ("Osimertinib", "Non-small cell lung cancer"),
    ("Erlotinib", "Non-small cell lung cancer"),
    ("Crizotinib", "Non-small cell lung cancer"),
    ("Alectinib", "Non-small cell lung cancer"),
    ("Pembrolizumab", "Non-small cell lung cancer"),
    ("Imatinib", "Chronic myeloid leukemia"),
    ("Dasatinib", "Chronic myeloid leukemia"),
    ("Nilotinib", "Chronic myeloid leukemia"),
    ("Midostaurin", "Acute myeloid leukemia"),
    ("Vemurafenib", "Melanoma"),
    ("Dabrafenib", "Melanoma"),
    ("Pembrolizumab", "Melanoma"),
    ("Nivolumab", "Melanoma"),
    ("Ipilimumab", "Melanoma"),
    ("Cetuximab", "Colorectal cancer"),
    ("Bevacizumab", "Colorectal cancer"),
    ("Imatinib mesylate (GIST use)", "Gastrointestinal stromal tumor"),
    ("Sunitinib", "Gastrointestinal stromal tumor"),
    ("Sunitinib", "Renal cell carcinoma"),
    ("Sorafenib", "Renal cell carcinoma"),
    ("Sorafenib", "Hepatocellular carcinoma"),
    ("Bevacizumab", "Renal cell carcinoma"),
    ("Rituximab", "Diffuse large B-cell lymphoma"),
    ("Rituximab", "Chronic lymphocytic leukemia"),
    ("Rituximab", "Non-Hodgkin lymphoma"),
    ("Olaparib", "Ovarian cancer"),
    ("Niraparib", "Ovarian cancer"),
    ("Olaparib", "HER2-positive breast cancer"),
    ("Enzalutamide", "Prostate cancer"),
    ("Abiraterone", "Prostate cancer"),
    ("Lenalidomide", "Multiple myeloma"),
    ("Bortezomib", "Multiple myeloma"),
    ("Atezolizumab", "Bladder cancer"),
    ("Pembrolizumab", "Bladder cancer"),
    ("Cetuximab", "Head and neck squamous cell carcinoma"),
    ("Pembrolizumab", "Head and neck squamous cell carcinoma"),
    ("Ruxolitinib", "Acute myeloid leukemia"),
    ("Everolimus", "Renal cell carcinoma"),
    ("Bevacizumab", "Pancreatic ductal adenocarcinoma"),
]

# (Drug name, Gene symbol)
TARGETS = [
    ("Trastuzumab", "ERBB2"),
    ("Pertuzumab", "ERBB2"),
    ("Trastuzumab emtansine (T-DM1)", "ERBB2"),
    ("Tamoxifen", "ESR1"),
    ("Letrozole", "ESR1"),
    ("Osimertinib", "EGFR"),
    ("Erlotinib", "EGFR"),
    ("Cetuximab", "EGFR"),
    ("Imatinib", "BCR::ABL1"),
    ("Imatinib", "KIT"),
    ("Imatinib", "PDGFRA"),
    ("Dasatinib", "BCR::ABL1"),
    ("Nilotinib", "BCR::ABL1"),
    ("Vemurafenib", "BRAF"),
    ("Dabrafenib", "BRAF"),
    ("Bevacizumab", "VEGFA"),
    ("Sunitinib", "VEGFA"),
    ("Sunitinib", "KIT"),
    ("Sorafenib", "VEGFA"),
    ("Rituximab", "CD20 (MS4A1)"),
    ("Olaparib", "PARP1"),
    ("Niraparib", "PARP1"),
    ("Enzalutamide", "AR"),
    ("Abiraterone", "AR"),
    ("Pembrolizumab", "PD-1 (PDCD1)"),
    ("Nivolumab", "PD-1 (PDCD1)"),
    ("Atezolizumab", "PD-L1 (CD274)"),
    ("Ipilimumab", "CTLA-4"),
    ("Crizotinib", "ALK"),
    ("Crizotinib", "MET"),
    ("Alectinib", "ALK"),
    ("Imatinib mesylate (GIST use)", "KIT"),
    ("Imatinib mesylate (GIST use)", "PDGFRA"),
    ("Midostaurin", "FLT3"),
    ("Ruxolitinib", "JAK2"),
    ("Everolimus", "MTOR"),
]

# (Gene symbol, Disease name)
ASSOCIATED_WITH = [
    ("ERBB2", "HER2-positive breast cancer"),
    ("ESR1", "Hormone receptor-positive breast cancer"),
    ("BRCA1", "Ovarian cancer"),
    ("BRCA2", "Ovarian cancer"),
    ("BRCA1", "Triple-negative breast cancer"),
    ("BRCA2", "HER2-positive breast cancer"),
    ("TP53", "Triple-negative breast cancer"),
    ("EGFR", "Non-small cell lung cancer"),
    ("KRAS", "Non-small cell lung cancer"),
    ("KRAS", "Colorectal cancer"),
    ("KRAS", "Pancreatic ductal adenocarcinoma"),
    ("ALK", "Non-small cell lung cancer"),
    ("BCR::ABL1", "Chronic myeloid leukemia"),
    ("BRAF", "Melanoma"),
    ("BRAF", "Colorectal cancer"),
    ("PIK3CA", "Hormone receptor-positive breast cancer"),
    ("KIT", "Gastrointestinal stromal tumor"),
    ("PDGFRA", "Gastrointestinal stromal tumor"),
    ("FLT3", "Acute myeloid leukemia"),
    ("JAK2", "Multiple myeloma"),
    ("AR", "Prostate cancer"),
    ("PD-L1 (CD274)", "Non-small cell lung cancer"),
    ("PD-L1 (CD274)", "Bladder cancer"),
    ("CD20 (MS4A1)", "Diffuse large B-cell lymphoma"),
    ("CD20 (MS4A1)", "Chronic lymphocytic leukemia"),
    ("MET", "Non-small cell lung cancer"),
    ("VEGFA", "Renal cell carcinoma"),
]

# (Disease name, Symptom name)
HAS_SYMPTOM = [
    ("HER2-positive breast cancer", "Breast lump"),
    ("Hormone receptor-positive breast cancer", "Breast lump"),
    ("Triple-negative breast cancer", "Breast lump"),
    ("Non-small cell lung cancer", "Persistent cough"),
    ("Non-small cell lung cancer", "Unintended weight loss"),
    ("Chronic myeloid leukemia", "Fatigue"),
    ("Acute myeloid leukemia", "Fatigue"),
    ("Acute myeloid leukemia", "Bone pain"),
    ("Melanoma", "Unintended weight loss"),
    ("Colorectal cancer", "Abdominal pain"),
    ("Gastrointestinal stromal tumor", "Abdominal pain"),
    ("Renal cell carcinoma", "Hematuria"),
    ("Bladder cancer", "Hematuria"),
    ("Diffuse large B-cell lymphoma", "Lymphadenopathy"),
    ("Diffuse large B-cell lymphoma", "Night sweats"),
    ("Non-Hodgkin lymphoma", "Lymphadenopathy"),
    ("Non-Hodgkin lymphoma", "Night sweats"),
    ("Chronic lymphocytic leukemia", "Lymphadenopathy"),
    ("Ovarian cancer", "Abdominal pain"),
    ("Multiple myeloma", "Bone pain"),
    ("Hepatocellular carcinoma", "Jaundice"),
    ("Pancreatic ductal adenocarcinoma", "Jaundice"),
    ("Pancreatic ductal adenocarcinoma", "Abdominal pain"),
]

# (Drug name, Trial id)
TESTED_IN = [
    ("Trastuzumab", "NCT00281658"),
    ("Osimertinib", "NCT02772763"),
    ("Imatinib", "NCT00006343"),
    ("Pembrolizumab", "NCT01584648"),
    ("Pembrolizumab", "NCT02008227"),
    ("Olaparib", "NCT01844986"),
    ("Vemurafenib", "NCT00738647"),
    ("Cetuximab", "NCT00075244"),
    ("Enzalutamide", "NCT01639508"),
    ("Alectinib", "NCT02181738"),
    ("Crizotinib", "NCT02181738"),
    ("Midostaurin", "NCT01120184"),
    ("Bevacizumab", "NCT00355706"),
]

# (Trial id, Disease name)
STUDIES = [
    ("NCT00281658", "HER2-positive breast cancer"),
    ("NCT02772763", "Non-small cell lung cancer"),
    ("NCT00006343", "Chronic myeloid leukemia"),
    ("NCT01584648", "Melanoma"),
    ("NCT02008227", "Non-small cell lung cancer"),
    ("NCT01844986", "Ovarian cancer"),
    ("NCT00738647", "Melanoma"),
    ("NCT00075244", "Colorectal cancer"),
    ("NCT01639508", "Prostate cancer"),
    ("NCT02181738", "Non-small cell lung cancer"),
    ("NCT01120184", "Acute myeloid leukemia"),
    ("NCT00355706", "Colorectal cancer"),
]

# (Drug name, Drug name) - known/documented interactions or combination regimens
INTERACTS_WITH = [
    ("Trastuzumab", "Pertuzumab"),
    ("Ipilimumab", "Nivolumab"),
    ("Dabrafenib", "Vemurafenib"),  # both BRAF inhibitors, not co-administered - class caution
    ("Palbociclib", "Letrozole"),
    ("Bevacizumab", "Cetuximab"),
]

import pandas as pd
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Enterprise EDMS - Construction & Data Centres",
    page_icon="🏗️",
    layout="wide",
)

# Initialize Session State Defaults
if "current_user" not in st.session_state:
  st.session_state.current_user = None

if "project_info" not in st.session_state:
  st.session_state.project_info = {
      "projectCode": "ALP",
      "companyCode": "GW",
      "locationCode": "IND",
  }

if "stages" not in st.session_state:
  st.session_state.stages = [
      {"code": "MP", "name": "Master Planning", "date": "15-Jan-2026"},
      {"code": "CD", "name": "Concept Design", "date": "15-May-2026"},
      {"code": "SD", "name": "Schematic Design", "date": "30-Jul-2026"},
      {"code": "DD", "name": "Detailed Design", "date": "30-Aug-2026"},
  ]

if "wbs_hierarchy" not in st.session_state:
  st.session_state.wbs_hierarchy = {
      "Architectural": [
          "General",
          "General Arrangement",
          "Schedule",
          "Details",
          "Site Layout",
          "Bill of Quantities",
          "Building Elevation",
          "Building Section",
          "3D Renders and BIM",
      ],
      "Structural": [
          "General",
          "Loading Diagrams",
          "Plans",
          "Section",
          "Calculation and Reports",
      ],
      "Civil": ["General", "Layout", "Section and Details"],
      "Mechanical": [
          "General",
          "Layout",
          "Chilled Water System",
          "Refrigerant System",
          "Smoke Extract System",
          "Fume Extract System",
          "Ventilation System",
          "Air Conditioning System Equipments",
          "Fire Protection System",
          "Fuel System",
          "Domestic Water Supply System",
          "Drainage System",
          "Calculation and Reports",
      ],
      "Electrical": [
          "General",
          "Layout",
          "Single Line Diagram",
          "Calculation and Reports",
      ],
      "Low Current": [
          "General",
          "Security System",
          "Fire Alarm System",
          "Monitoring & Controlling System",
          "Telecom System",
          "Calculation and Reports",
      ],
      "General": ["General"],
      "ELV": ["General"],
      "PHE": ["General"],
      "Fire Fighting": ["General"],
  }

if "lookups" not in st.session_state:
  st.session_state.lookups = {
      "buildings": [
          {"code": "GI", "name": "General Infrastructure"},
          {"code": "DC", "name": "Data Centre Building 1"},
          {"code": "AD", "name": "Administration Building"},
      ],
      "floors": [
          {"code": "B1", "name": "Basement 1"},
          {"code": "00", "name": "Ground Floor"},
          {"code": "1F", "name": "First Floor"},
          {"code": "RF", "name": "Roof Level"},
      ],
      "types": [
          {"code": "PL", "name": "Plan"},
          {"code": "DR", "name": "Drawing"},
          {"code": "CS", "name": "Calculation Sheet"},
          {"code": "SP", "name": "Specification"},
      ],
  }

if "documents" not in st.session_state:
  st.session_state.documents = [
      {
          "id": "doc-1",
          "title": "Architectural Foundation Plan",
          "discipline": "Architectural",
          "subCategory": "General Arrangement",
          "building": "GI",
          "floor": "00",
          "type": "PL",
          "stages": {"MP": False, "CD": True, "SD": False, "DD": True},
          "stageSequences": {"CD": "001", "DD": "001"},
          "revision": "00",
          "status": "DRAFT",
      },
      {
          "id": "doc-2",
          "title": "Site Master Layout & Finishes",
          "discipline": "Architectural",
          "subCategory": "Site Layout",
          "building": "GI",
          "floor": "00",
          "type": "PL",
          "stages": {"MP": True, "CD": True, "SD": False, "DD": False},
          "stageSequences": {"MP": "001", "CD": "002"},
          "revision": "00",
          "status": "APPROVED",
      },
      {
          "id": "doc-3",
          "title": "Chilled Water Piping Layout - Level 1",
          "discipline": "Mechanical",
          "subCategory": "Chilled Water System",
          "building": "DC",
          "floor": "1F",
          "type": "PL",
          "stages": {"MP": False, "CD": True, "SD": True, "DD": False},
          "stageSequences": {"CD": "001", "SD": "001"},
          "revision": "00",
          "status": "ISSUED",
      },
  ]


# Helper Functions
def get_disc_short_code(disc):
  mapping = {
      "Architectural": "AR",
      "Structural": "ST",
      "Civil": "CV",
      "Mechanical": "ME",
      "Electrical": "EL",
      "Low Current": "LC",
      "General": "GN",
      "ELV": "EV",
      "PHE": "PH",
      "Fire Fighting": "FF",
  }
  return mapping.get(disc, disc[:2].upper())


def get_numbering_group_key(doc, stage_code):
  p = st.session_state.project_info
  project = p.get("projectCode", "ALP")
  company = p.get("companyCode", "GW")
  location = p.get("locationCode", "IND")
  disc_code = get_disc_short_code(doc["discipline"])
  sub_cat = doc.get("subCategory", "General")
  sub_code = sub_cat[:2].upper() if sub_cat else "GN"

  return "-".join([
      project,
      company,
      location,
      stage_code,
      disc_code,
      doc["building"],
      doc["floor"],
      doc["type"],
      sub_code,
  ])


def get_next_sequence_for_doc(doc, stage_code, doc_list=None):
  if doc_list is None:
    doc_list = st.session_state.documents
  group_key = get_numbering_group_key(doc, stage_code)
  count = 0
  for d in doc_list:
    if d.get("stages", {}).get(stage_code, False):
      if get_numbering_group_key(d, stage_code) == group_key:
        count += 1
        if d.get("id") == doc.get("id"):
          return f"{count:03d}"
  return f"{count + 1:03d}"


def generate_code(doc, stage_code):
  group_key = get_numbering_group_key(doc, stage_code)
  seq = doc.get("stageSequences", {}).get(
      stage_code, get_next_sequence_for_doc(doc, stage_code)
  )
  rev = doc.get("revision", "00")
  return f"{group_key}-{seq}-{rev}"


# ----------------------------------------------------
# AUTHENTICATION SCREEN
# ----------------------------------------------------
if st.session_state.current_user is None:
  st.title("🏗️ Enterprise EDMS - Construction & Data Centres")
  st.markdown("### Select your portal to log in")

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("🛡️ Document Controller")
    st.write(
        "Master administrator access to WBS registers, project submission"
        " dates, and numbering sequence engines."
    )
    if st.button("Login as Controller", type="primary", use_container_width=True):
      st.session_state.current_user = "controller"
      st.rerun()

  with col2:
    st.subheader("👷 Discipline Teams")
    st.write(
        "Submit drawings, bulk-paste lists from Excel, and manage stage"
        " deliverables."
    )
    active_disciplines = list(st.session_state.wbs_hierarchy.keys())
    selected_disc = st.selectbox(
        "Select Discipline (Level 1)", active_disciplines
    )
    if st.button(
        "Enter Discipline Portal", type="secondary", use_container_width=True
    ):
      st.session_state.current_user = selected_disc
      st.rerun()

# ----------------------------------------------------
# DISCIPLINE PORTAL
# ----------------------------------------------------
elif st.session_state.current_user != "controller":
  current_disc = st.session_state.current_user
  st.sidebar.title(f"👤 {current_disc} Portal")
  if st.sidebar.button("🚪 Logout"):
    st.session_state.current_user = None
    st.rerun()

  st.title(f"👷 {current_disc} Discipline Workspace")
  st.markdown(
      "Manage document submissions, categories, and stage deliverable"
      " checkboxes."
  )

  available_subcats = st.session_state.wbs_hierarchy.get(
      current_disc, ["General"]
  )
  buildings = [b["code"] for b in st.session_state.lookups["buildings"]]
  floors = [f["code"] for f in st.session_state.lookups["floors"]]
  types = [t["code"] for t in st.session_state.lookups["types"]]
  stage_codes = [s["code"] for s in st.session_state.stages]

  tab1, tab2 = st.tabs(
      ["➕ Add Document(s)", "📋 My Submitted Documents Register"]
  )

  with tab1:
    st.subheader("Submit New Document")
    with st.form("single_doc_form"):
      title = st.text_input(
          "Document Title (Level 3)",
          placeholder="e.g., Ground Floor Lighting Layout & Circuiting",
      )
      col_a, col_b = st.columns(2)
      with col_a:
        sub_cat = st.selectbox("Level 2 Category", available_subcats)
        building = st.selectbox("Building", buildings)
      with col_b:
        floor = st.selectbox("Floor Level", floors)
        doc_type = st.selectbox("Document Type", types)

      st.markdown("**Applicable Stages:**")
      stage_cols = st.columns(len(stage_codes))
      selected_stages = {}
      for idx, st_code in enumerate(stage_codes):
        with stage_cols[idx]:
          selected_stages[st_code] = st.checkbox(
              st_code, value=(st_code == "CD")
          )

      submitted = st.form_submit_button("Submit Single Document")
      if submitted:
        if not title.strip():
          st.error("Please provide a document title.")
        else:
          dummy_doc = {
              "discipline": current_disc,
              "subCategory": sub_cat,
              "building": building,
              "floor": floor,
              "type": doc_type,
          }
          stage_seqs = {}
          for st_code, active in selected_stages.items():
            if active:
              stage_seqs[st_code] = get_next_sequence_for_doc(dummy_doc, st_code)

          new_doc = {
              "id": f"doc-{len(st.session_state.documents) + 1}",
              "title": title.strip(),
              "discipline": current_disc,
              "subCategory": sub_cat,
              "building": building,
              "floor": floor,
              "type": doc_type,
              "stages": selected_stages,
              "stageSequences": stage_seqs,
              "revision": "00",
              "status": "DRAFT",
          }
          st.session_state.documents.append(new_doc)
          st.success("Document added successfully!")
          st.rerun()

    st.divider()
    st.subheader("📥 Excel Bulk Copy-Paste Import")
    with st.form("bulk_import_form"):
      bulk_sub_cat = st.selectbox(
          "Level 2 Category (For all pasted items)",
          available_subcats,
          key="bulk_sub",
      )
      col_c, col_d, col_e = st.columns(3)
      with col_c:
        bulk_building = st.selectbox(
            "Building", buildings, key="bulk_building"
        )
      with col_d:
        bulk_floor = st.selectbox("Floor Level", floors, key="bulk_floor")
      with col_e:
        bulk_type = st.selectbox("Document Type", types, key="bulk_type")

      pasted_text = st.text_area(
          "Paste continuous Excel rows of Document Titles here:",
          placeholder="Ground Floor Lighting Layout Plan\nMain Cable Routing"
          " Diagram\nTransformer Sizing Sheet",
      )
      bulk_submitted = st.form_submit_button("Import Bulk List")

      if bulk_submitted:
        lines = [l.strip() for l in pasted_text.split("\n") if l.strip()]
        if not lines:
          st.warning("Please paste at least one line of text.")
        else:
          for idx, line in enumerate(lines):
            dummy_doc = {
                "discipline": current_disc,
                "subCategory": bulk_sub_cat,
                "building": bulk_building,
                "floor": bulk_floor,
                "type": bulk_type,
            }
            stages_obj = {
                "MP": False,
                "CD": True,
                "SD": False,
                "DD": False,
            }
            stage_seqs = {
                "CD": get_next_sequence_for_doc(dummy_doc, "CD")
            }

            new_doc = {
                "id": f"doc-bulk-{len(st.session_state.documents)}-{idx}",
                "title": line,
                "discipline": current_disc,
                "subCategory": bulk_sub_cat,
                "building": bulk_building,
                "floor": bulk_floor,
                "type": bulk_type,
                "stages": stages_obj,
                "stageSequences": stage_seqs,
                "revision": "00",
                "status": "DRAFT",
            }
            st.session_state.documents.append(new_doc)
          st.success(
              f"Successfully imported {len(lines)} documents from bulk text!"
          )
          st.rerun()

  with tab2:
    st.subheader(f"Documents Submitted by {current_disc}")
    my_docs = [
        d for d in st.session_state.documents if d["discipline"] == current_disc
    ]

    if not my_docs:
      st.info("No documents submitted yet.")
    else:
      for idx, doc in enumerate(my_docs):
        with st.container():
          col1, col2, col3 = st.columns([3, 2, 1])
          with col1:
            st.write(f"**{idx + 1}. {doc['title']}**")
            st.caption(
                f"Category: {doc.get('subCategory', 'General')} | Building:"
                f" {doc['building']} | Floor: {doc['floor']}"
            )
          with col2:
            # Stage checkboxes
            st.write("Stages:")
            cols = st.columns(len(stage_codes))
            for i, st_code in enumerate(stage_codes):
              with cols[i]:
                current_val = doc.get("stages", {}).get(st_code, False)
                new_val = st.checkbox(
                    st_code, value=current_val, key=f"chk_{doc['id']}_{st_code}"
                )
                if new_val != current_val:
                  doc["stages"][st_code] = new_val
                  if new_val and st_code not in doc.get(
                      "stageSequences", {}
                  ):
                    if "stageSequences" not in doc:
                      doc["stageSequences"] = {}
                    doc["stageSequences"][st_code] = (
                        get_next_sequence_for_doc(doc, st_code)
                    )
                  st.rerun()
          with col3:
            if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
              st.session_state.documents = [
                  d for d in st.session_state.documents if d["id"] != doc["id"]
              ]
              st.rerun()
          st.divider()

# ----------------------------------------------------
# DOCUMENT CONTROLLER MASTER DASHBOARD
# ----------------------------------------------------
else:
  st.sidebar.title("🛡️ Controller Panel")
  if st.sidebar.button("🚪 Logout"):
    st.session_state.current_user = None
    st.rerun()

  controller_nav = st.sidebar.radio(
      "Navigation",
      [
          "📋 WBS Registers",
          "🔄 Sequence Refresh Engine",
          "🗄️ Lookups Manager (CRUD)",
          "🏗️ WBS Level Provisions",
          "⚙️ Project Details & Stages",
          "📊 Export to Excel",
      ],
  )

  p_info = st.session_state.project_info
  st.title("🛡️ Document Controller Master Dashboard")
  st.caption(
      f"Project: {p_info['projectCode']} | Company: {p_info['companyCode']} |"
      f" Location: {p_info['locationCode']}"
  )

  if controller_nav == "📋 WBS Registers":
    stage_tabs = st.tabs([s["name"] for s in st.session_state.stages])
    for s_idx, stage in enumerate(st.session_state.stages):
      st_code = stage["code"]
      with stage_tabs[s_idx]:
        st.info(
            f"Planned Submission Date for {stage['name']} ({st_code}):"
            f" **{stage['date']}**"
        )

        stage_docs = [
            d for d in st.session_state.documents if d.get("stages", {}).get(st_code, False)
        ]
        if not stage_docs:
          st.warning(f"No documents assigned to stage {stage['name']}.")
        else:
          # Group by Level 1 (Discipline)
          l1_groups = {}
          for d in stage_docs:
            l1 = d["discipline"]
            if l1 not in l1_groups:
              l1_groups[l1] = []
            l1_groups[l1].append(d)

          for l1_disc, l1_docs in l1_groups.items():
            with st.expander(f"📁 Discipline (Level 1): {l1_disc} ({len(l1_docs)} deliverables)", expanded=True):
              # Group by Level 2 (SubCategory)
              l2_groups = {}
              for d in l1_docs:
                l2 = d.get("subCategory", "General")
                if l2 not in l2_groups:
                  l2_groups[l2] = []
                l2_groups[l2].append(d)

              for l2_cat, l2_docs in l2_groups.items():
                st.markdown(f"**Level 2 Category: {l2_cat}**")
                table_data = []
                for i, doc in enumerate(l2_docs):
                  table_data.append({
                      "Sr. No.": i + 1,
                      "Document Title (Level 3)": doc["title"],
                      "Document Number (ISO)": generate_code(doc, st_code),
                      "Planned Date": stage["date"],
                      "Rev": doc.get("revision", "00"),
                      "Status": doc.get("status", "DRAFT"),
                  })
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

  elif controller_nav == "🔄 Sequence Refresh Engine":
    st.subheader("Document Sequence & Refresh Engine")
    st.write(
        "Recalculate and synchronize sequence numbers per numbering group."
    )

    if st.button("🚀 Run Full Sequence Refresh"):
      for doc in st.session_state.documents:
        for st_code in doc.get("stages", {}):
          if doc["stages"][st_code]:
            if "stageSequences" not in doc:
              doc["stageSequences"] = {}
            doc["stageSequences"][st_code] = get_next_sequence_for_doc(
                doc, st_code
            )
      st.success("Full sequence register successfully refreshed!")

  elif controller_nav == "🗄️ Lookups Manager (CRUD)":
    st.subheader("Reference Codes Lookup Manager")

    lookup_types = {
        "buildings": "Building Codes",
        "floors": "Floor Level Codes",
        "types": "Document Type Codes",
    }

    for key, title in lookup_types.items():
      st.markdown(f"### {title}")
      items = st.session_state.lookups[key]

      # Display table
      df_lookups = pd.DataFrame(items)
      st.dataframe(df_lookups, use_container_width=True)

      with st.form(f"add_{key}_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
          new_code = st.text_input("New Code", key=f"code_{key}")
        with col2:
          new_name = st.text_input("New Description Name", key=f"name_{key}")
        with col3:
          st.write("")
          add_btn = st.form_submit_button(f"Add {title[:-6]}")

        if add_btn:
          if new_code and new_name:
            st.session_state.lookups[key].append({
                "code": new_code.upper(),
                "name": new_name,
            })
            st.success(f"Added new item to {title}!")
            st.rerun()
          else:
            st.error("Please fill in both code and description.")

  elif controller_nav == "🏗️ WBS Level Provisions":
    st.subheader("WBS Hierarchy Provision Manager")
    st.write("Manage Level 1 Disciplines and Level 2 Categories.")

    # Level 1 Management
    st.markdown("### Level 1 - Disciplines")
    new_l1 = st.text_input("New Discipline Name")
    if st.button("Add Level 1 Discipline"):
      if new_l1 and new_l1 not in st.session_state.wbs_hierarchy:
        st.session_state.wbs_hierarchy[new_l1] = ["General"]
        st.success(f"Added Discipline '{new_l1}'")
        st.rerun()

    st.write(
        "Current Disciplines:", list(st.session_state.wbs_hierarchy.keys())
    )
    st.divider()

    # Level 2 Management
    st.markdown("### Level 2 - Categories")
    selected_l1_for_l2 = st.selectbox(
        "Select Discipline", list(st.session_state.wbs_hierarchy.keys())
    )
    new_l2 = st.text_input("New Category Name")
    if st.button("Add Level 2 Category"):
      if new_l2 and new_l2 not in st.session_state.wbs_hierarchy[selected_l1_for_l2]:
        st.session_state.wbs_hierarchy[selected_l1_for_l2].append(new_l2)
        st.success(f"Added Category '{new_l2}' to {selected_l1_for_l2}")
        st.rerun()

  elif controller_nav == "⚙️ Project Details & Stages":
    st.subheader("Project Details & Stage Management")

    with st.form("project_details_form"):
      pc = st.text_input(
          "Project Code", value=st.session_state.project_info["projectCode"]
      )
      cc = st.text_input(
          "Company Code", value=st.session_state.project_info["companyCode"]
      )
      lc = st.text_input(
          "Location Code", value=st.session_state.project_info["locationCode"]
      )

      st.markdown("### Project Stages & Submission Dates")
      updated_stages = []
      for idx, stg in enumerate(st.session_state.stages):
        col1, col2, col3 = st.columns(3)
        with col1:
          sc = st.text_input(f"Code {idx}", value=stg["code"], key=f"stg_c_{idx}")
        with col2:
          sn = st.text_input(f"Name {idx}", value=stg["name"], key=f"stg_n_{idx}")
        with col3:
          sd = st.text_input(f"Date {idx}", value=stg["date"], key=f"stg_d_{idx}")
        updated_stages.append({"code": sc, "name": sn, "date": sd})

      save_proj = st.form_submit_button("Save Project Configuration")
      if save_proj:
        st.session_state.project_info = {
            "projectCode": pc.upper(),
            "companyCode": cc.upper(),
            "locationCode": lc.upper(),
        }
        st.session_state.stages = updated_stages
        st.success("Project configuration updated successfully!")
        st.rerun()

  elif controller_nav == "📊 Export to Excel":
    st.subheader("Export Document Register")
    st.write("Download the master document register as a CSV file.")

    export_data = []
    for idx, doc in enumerate(st.session_state.documents):
      export_data.append({
          "Sr. No.": idx + 1,
          "Document Title": doc["title"],
          "Discipline (Level 1)": doc["discipline"],
          "Category (Level 2)": doc.get("subCategory", "General"),
          "Building": doc["building"],
          "Floor": doc["floor"],
          "Type": doc["type"],
          "Revision": doc.get("revision", "00"),
          "Status": doc.get("status", "DRAFT"),
      })

    df_export = pd.DataFrame(export_data)
    csv_data = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Master Document Register (CSV)",
        data=csv_data,
        file_name=f"EDMS_Register_{st.session_state.project_info['projectCode']}.csv",
        mime="text/csv",
    )

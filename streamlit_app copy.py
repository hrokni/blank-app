import json
from jsonschema import validate
from pydantic import BaseModel
from textwrap import dedent
import os
from openai import OpenAI
import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

client = OpenAI(
    base_url="http://91.134.19.242:8000/v1",
    api_key="EMPTY",
)

class Output(BaseModel):
    answer: str


def generate_json_schema_strict_false(prompt,history):
    response = client.chat.completions.create(
        model="hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4",
        messages=[
            {
                "role": "system",
                "content": """
You are reactflow json generator, strictly follow below json schema and generate json for give question.

Rules:
1. Only Generate one final json and no explanation
2. If there is current json, then rewrite or update the existing

Schema:
{
  "type": "object",
  "properties": {
    "nodes": {
      "type": "array",
      "description": "List of nodes in the flow",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique ID of the node"
          },
          "pos": {
            "type": "array",
            "items": [
              {
                "type": "integer",
                "description": "Position X"
              },
              {
                "type": "integer",
                "description": "Position Y"
              }
            ],
            "minItems": 2,
            "maxItems": 2,
            "description": "Tuple[float, float] : Position of the node in the canvas"
          },
          "data": {
            "type": "object",
            "properties": {
              "content": {
                "type": "string",
                "description": "Content of the node"
              }
            },
            "required": ["content"],
            "description": "Data associated with the node"
          },
          "node_type": {
            "type": "string",
            "description": "Type of the node, e.g., 'input', 'default'"
          },
          "source_position": {
            "type": "string",
            "description": "Optional incoming direction, e.g., 'left', 'right'"
          },
          "target_position": {
            "type": "string",
            "description": "Optional incoming direction, e.g., 'left', 'right'"
          }
        },
        "required": ["id", "pos", "data", "node_type"],
        "description": "Represents a single node in the flow"
      }
    },
    "edges": {
      "type": "array",
      "description": "List of edges between nodes",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique ID of the edge"
          },
          "source": {
            "type": "string",
            "description": "ID of the source node"
          },
          "target": {
            "type": "string",
            "description": "ID of the target node"
          },
          "animated": {
            "type": "boolean",
            "description": "Indicates if the edge is animated",
            "default": false
          }
        },
        "required": ["id", "source", "target"],
        "description": "Represents a connection (edge) between two nodes"
      }
    }
  },
  "required": ["nodes", "edges"]
}


Current JSON:
{history}

Question:
""",
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    return data


import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
import random
from uuid import uuid4



#if st.button("Add node"):
#  data = generate_json_schema_strict_false("")
#  js = st.json(data)
#  for node in data["nodes"]:
#    new_node = StreamlitFlowNode(str(node["id"]), (node["pos"][0], node["pos"][1]), {'content': node["data"]["content"]}, 'default', 'right', 'left')
#    st.session_state.curr_state.nodes.append(new_node)
#    st.rerun()
json_nodes =[]
if 'json_nodes' not in st.session_state:
   st.session_state.json_nodes = json_nodes
   
if 'curr_state' not in st.session_state:
    print("initilise")
    nodes = [StreamlitFlowNode("1", (0, 0), {'content': 'Node 1'}, 'input', 'right')]
    edges = []
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)

prompt = st.chat_input("Say something")
if prompt:
  print("prompt sent")
  print(st.session_state.json_nodes)
  data = generate_json_schema_strict_false(prompt,st.session_state.json_nodes)
  st.session_state.json_nodes = data
  st.session_state.curr_state.nodes = []
  for node in data["nodes"]:
    print(node["id"])
    new_node = StreamlitFlowNode(str(node["id"]), (node["pos"][0], node["pos"][1]), {'content': node["data"]["content"]}, 'default', 'right', 'left')
    st.session_state.curr_state.nodes.append(new_node)
  st.rerun()

st.session_state.curr_state = streamlit_flow('example_flow', 
                                st.session_state.curr_state, 
                                layout=TreeLayout(direction='right'), 
                                fit_view=True, 
                                height=500, 
                                enable_node_menu=True,
                                enable_edge_menu=True,
                                enable_pane_menu=True,
                                get_edge_on_click=True,
                                get_node_on_click=True, 
                                show_minimap=True, 
                                hide_watermark=True, 
                                allow_new_edges=True,
                                min_zoom=0.1)
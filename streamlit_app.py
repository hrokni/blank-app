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

math_tutor_prompt = """
    You are a helpful math tutor. You will be provided with a math problem,
    and your goal will be to output a step by step solution, along with a final answer.
    For each step, just provide the output as an equation use the explanation field to detail the reasoning.
"""

question = "how can I solve 8x + 7 = -23"

schema = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "explanation": {"type": "string"},
                    "output": {"type": "string"},
                },
                "required": ["explanation", "output"],
                "additionalProperties": False,
            },
        },
        "final_answer": {"type": "string"},
    },
    "required": ["steps", "final_answer"],
    "additionalProperties": False,
}


class Output(BaseModel):
    answer: str


def generate_json_schema_strict_false():
    schema = Output.model_json_schema()
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
[]

Question:
""",
            },

            {"role": "user", "content": "Add one load balancer"}
        ],
        temperature=0,
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    # validate(instance=data, schema=schema)
    return data


import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
import random
from uuid import uuid4



if st.button("Add node"):
  data = generate_json_schema_strict_false()
  js = st.json(data)
  print(data["nodes"])
  for node in data["nodes"]:
    print(node["id"])
    print(node["pos"][0])
    print(node["pos"][1])
    new_node = StreamlitFlowNode(str(node["id"]), (node["pos"][0], node["pos"][1]), {'content': node["data"]["content"]}, 'default', 'right', 'left')
    st.session_state.curr_state.nodes.append(new_node)
    st.rerun()
    #new_node = StreamlitFlowNode(str(f"st-flow-node_{uuid4()}"), (0, 0), {'content': 'Node 1'}, 'default', 'right', 'left')
    #st.text(st.session_state.curr_state.nodes)
    #st.text(new_node)
    #st.session_state.curr_state.nodes.append(new_node)
    #st.rerun()
    
if 'curr_state' not in st.session_state:
    nodes = [StreamlitFlowNode("1", (0, 0), {'content': 'Node 1'}, 'input', 'right'),
            StreamlitFlowNode("2", (1, 0), {'content': 'Node 2'}, 'default', 'right', 'left'),
            StreamlitFlowNode("3", (2, 0), {'content': 'Node 3'}, 'default', 'right', 'left'),
            ]
    edges = []
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)

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

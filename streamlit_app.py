import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState

# Initialize session state for the chatbot
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize state for the flow diagram
if 'flow_state' not in st.session_state:
    # Define initial nodes
    nodes = [
        StreamlitFlowNode(
            id='start',
            pos=(100, 100),
            data={'content': 'Start'},
            node_type='input',
            source_position='right',
            style={},  # Initialize with default style
        ),
        StreamlitFlowNode(
            id='end',
            pos=(500, 100),
            data={'content': 'End'},
            node_type='output',
            target_position='left',
            style={},  # Initialize with default style
        ),
    ]

    # Define initial edges
    edges = []

    # Create the flow state
    st.session_state.flow_state = StreamlitFlowState(nodes=nodes, edges=edges)

# Define functions for adding, removing, and changing node names

def add_node(node_name):
    node_id = node_name.lower()
    # Check if node already exists
    node_ids = [node.id for node in st.session_state.flow_state.nodes]
    if node_id in node_ids:
        return f"Node '{node_name}' already exists."
    else:
        # Add new node
        new_node = StreamlitFlowNode(
            id=node_id,
            pos=(300, 100),  # Adjust the position as needed
            data={'content': node_name},
            node_type='default',
            target_position='left',
            source_position='right',
            style={},
        )
        st.session_state.flow_state.nodes.append(new_node)

        # Connect the new node between 'start' and 'end'
        st.session_state.flow_state.edges.append(
            StreamlitFlowEdge(
                id=f'start-{node_id}',
                source='start',
                target=node_id,
            )
        )
        st.session_state.flow_state.edges.append(
            StreamlitFlowEdge(
                id=f'{node_id}-end',
                source=node_id,
                target='end',
            )
        )

        return f"Node '{node_name}' added."

def remove_node(node_name):
    node_id = node_name.lower()
    # Check if node exists
    node_ids = [node.id for node in st.session_state.flow_state.nodes]
    if node_id in node_ids:
        # Remove the node
        st.session_state.flow_state.nodes = [
            node for node in st.session_state.flow_state.nodes if node.id != node_id
        ]

        # Remove edges connected to the node
        st.session_state.flow_state.edges = [
            edge for edge in st.session_state.flow_state.edges
            if edge.source != node_id and edge.target != node_id
        ]

        return f"Node '{node_name}' removed."
    else:
        return f"Node '{node_name}' does not exist."

def change_node_name(old_name, new_name):
    old_node_id = old_name.lower()
    # Check if old node exists
    node_ids = [node.id for node in st.session_state.flow_state.nodes]
    if old_node_id in node_ids:
        # Update the node's content
        for node in st.session_state.flow_state.nodes:
            if node.id == old_node_id:
                node.data['content'] = new_name
        return f"Node '{old_name}' changed to '{new_name}'."
    else:
        return f"Node '{old_name}' does not exist."

# Create two columns for layout
col1, col2 = st.columns([1, 2])  # Adjust the ratio as needed

# Left column: Chatbot
with col1:
    st.header("Chatbot")

    # Create a container for messages
    message_container = st.container()

    # Input for user message with a form, placed at the bottom
    input_container = st.container()

    with input_container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Type your message:")
            submit_button = st.form_submit_button(label='Send')
            if submit_button and user_input:
                # Append user message to the conversation
                st.session_state.messages.append({'role': 'user', 'content': user_input})

                # Process the user input
                response = ""
                # Check if the message is "add [node_name]"
                if user_input.lower().startswith("add "):
                    node_name = user_input[4:].strip()
                    response = add_node(node_name)

                # Check if the message is "remove [node_name]"
                elif user_input.lower().startswith("remove "):
                    node_name = user_input[7:].strip()
                    response = remove_node(node_name)

                # Check if the message is "change [node_name] to [new_name]"
                elif user_input.lower().startswith("change "):
                    # Expected format: "change old_name to new_name"
                    parts = user_input[7:].strip().split(" to ", 1)
                    if len(parts) == 2:
                        old_name, new_name = parts
                        response = change_node_name(old_name.strip(), new_name.strip())
                    else:
                        response = "Please use the format 'change old_name to new_name'."

                else:
                    # Default bot response
                    response = f"You said: {user_input}"

                # Set 'selected' to True on the 'Start' node (id='1')
                for node in st.session_state.flow_state.nodes:
                    if node.id == 'start':
                            node.selected = True
                            node.style = {'border': '2px solid red'}
                # Append bot response to the conversation
                st.session_state.messages.append({'role': 'bot', 'content': response})

    # Display the conversation history above the input
    with message_container:
        for message in st.session_state.messages:
            is_user = message['role'] == 'user'
            alignment = 'user' if is_user else 'assistant'
            with st.chat_message(alignment):
                st.markdown(message['content'])

# Right column: ReactFlow diagram
with col2:
    st.header("ReactFlow Diagram")

    # Display the ReactFlow diagram
    st.session_state.flow_state = streamlit_flow(
        key='flow_diagram',
        state=st.session_state.flow_state,
        height=500,
        fit_view=True,
        show_controls=True,
        show_minimap=True,
    )

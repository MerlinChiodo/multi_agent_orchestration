import streamlit as st

def graph_dot():
    """Visualisierung des Prozesses mit Graphviz."""
    dot = r"""
    digraph G {
        rankdir=LR;
        node [
            shape=box,
            style="rounded,filled",
            color="#9ca3af",
            fillcolor="#f9fafb",
            fontname="Inter"
        ];

        input      [label="Input (Text)"];
        reader     [label="Reader (Notes)"];
        summarizer [label="Summarizer"];
        translator [label="Translator (DE/EN)"];
        keyword    [label="Keyword Extraction"];
        critic     [label="Critic"];
        quality    [label="Quality (F1)"];
        judge      [label="Judge"];
        aggregator [label="Judge Aggregate"];
        integrator [label="Integrator"];
        output     [label="Output (Structured, Summary, Critic, Meta)"];

        input -> reader -> summarizer -> translator -> keyword -> critic;
        critic -> quality -> judge -> aggregator -> integrator -> output;
        critic -> judge [label="kurze Summary", style="dashed"];
        critic -> summarizer [label="schlechter Critic Score", style="dotted"];
    }
    """.strip()
    st.graphviz_chart(dot, use_container_width=True)

## ReAct Agent From Scratch

Hand-built implementation of the ReAct pattern (Reasoning + Acting) for LLM agents, without any framework — the model alternates between reasoning steps and tool calls in a plain loop.

Source: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

![ReAct loop](./images/react.gif)

### Requirements

- Python 3.8+
- An OpenAI API key ([create one here](https://platform.openai.com/account/api-keys))

### Usage

```bash
pip install -r requirements.txt
python react_agent.py "<your question>"
```

Example:

```bash
python react_agent.py "I want to buy a keyboard and two monitors. How much will that cost?"
```

### Contents

- `react_agent.py` — the agent loop: system prompt, tools, and the THOUGHT/ACTION/PAUSE/OBSERVATION parsing loop.
- `notebooks/react-agent-from-scratch.ipynb` — step-by-step build adapted from [Simon Willison's ReAct pattern TIL](https://til.simonwillison.net/llms/python-react-pattern).
- `notebooks/react-agent-tutorial.ipynb` — a more detailed walkthrough of the same pattern, with its own tools and examples.

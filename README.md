# Data Visualization Skill

[![Atlassian license](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](LICENSE) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

An agent skill that makes your AI coding agent produce clean, publication-quality [Plotly](https://plotly.com/python/) charts in the Tufte tradition: light grids, no chart junk, one consistent palette, and a creation-date annotation on every chart. It works with any agent that supports the [Agent Skills](https://agentskills.io) format, including Claude Code and Codex.

Charts generated from a plain prompt tend to look different every time, because nothing fixes the colours, fonts, grid style or sizing. This skill gives the agent one editable style definition and a ready-made code pattern for each chart type, so every chart in a notebook or report is styled the same way. It also gives the agent chart selection guidance and styling rules that avoid common Plotly pitfalls, such as unsorted lines and low-contrast colours.

## Usage

Once the skill is installed, describe the chart you want. The agent loads the skill when the request involves charts or Plotly:

- "Make a bar chart of average sales by region from `df`."
- "Plot monthly active users by product as a line chart."
- "Which chart type should I use to show retention by signup cohort?"
- "Restyle this Plotly figure to match the visualization skill."

The agent writes the style preamble once (as its own notebook cell, or at the top of a script), then generates each chart from a short pattern. For example, a bar chart looks like this:

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Average sales by region"),
    showlegend=False,
))
fig.add_trace(go.Bar(x=df["region"], y=df["avg_sales"]))
fig.update_layout(xaxis_title="Region", yaxis_title="Average sales")
add_created_at_annotation(fig)  # bottom-right "Chart created: YYYY-MM-DD"
fig.show()
```

`get_layout()` and `add_created_at_annotation()` come from the preamble in [`skills/visualization/SKILL.md`](skills/visualization/SKILL.md).

## Installation

### Ask your agent

Open your agent in the project where you want charts, and say any variation of:

> Use the README.md at https://github.com/atlassian-labs/data-visualization-skill to install the visualization skill.

### Manual install

Requirements: `plotly` and `pandas`, plus `kaleido` only if you want to export static images (`pip install kaleido`).

Clone the repository, then copy the `skills/visualization` folder into your agent's skills directory:

```bash
git clone https://github.com/atlassian-labs/data-visualization-skill.git
```

| Agent | Install for all projects | Install for one project |
| --- | --- | --- |
| Claude Code | `cp -R data-visualization-skill/skills/visualization ~/.claude/skills/` | `cp -R data-visualization-skill/skills/visualization <project>/.claude/skills/` |
| Codex | `cp -R data-visualization-skill/skills/visualization ~/.agents/skills/` | `cp -R data-visualization-skill/skills/visualization <project>/.agents/skills/` |

## Documentation

### Supported chart types

Bar, grouped bar, stacked bar, horizontal bar, line, bar + line, area, scatter, bubble, heatmap, cohort heatmap, histogram, boxplot, violin, pie, funnel, waterfall, Sankey, treemap, sunburst, indicator (KPI tiles), dumbbell, and radar. Code for each is in [`skills/visualization/references/chart-patterns.md`](skills/visualization/references/chart-patterns.md).

### Customise

Everything a chart inherits (colours, fonts, default size) sits in the `STYLE SETTINGS` block of the preamble in [`skills/visualization/SKILL.md`](skills/visualization/SKILL.md). Edit that block to restyle every chart. The default colours are the `Lupi` palette from [MoMAColors](https://github.com/BlakeRMills/MoMAColors) (MIT), and the default font stack is Helvetica Neue, Helvetica, Arial.

### Repository layout

```
README.md
AGENTS.md                              # placeholder for agent instructions
CLAUDE.md                              # symlink to AGENTS.md
skills/
  visualization/
    SKILL.md                           # skill definition, preamble, rules
    references/
      chart-patterns.md                # code patterns for every chart type
.claude/skills/visualization           # symlink to skills/visualization
```

## Project status

This is an Atlassian Labs project, published as a reference for the data science community. It is maintained on a best-effort basis: issues and pull requests are reviewed as the team has time, and the project may be archived if it goes unmaintained.

## Contributions

Contributions to Data Visualization Skill are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details. To report a security issue, see [SECURITY.md](SECURITY.md).

## License

Copyright (c) 2026 Atlassian US., Inc.
Apache 2.0 licensed, see [LICENSE](LICENSE) file.

<br/>

[![With ❤️ from Atlassian](https://raw.githubusercontent.com/atlassian-internal/oss-assets/master/banner-with-thanks.png)](https://www.atlassian.com)

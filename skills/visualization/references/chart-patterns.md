# Chart Patterns

Complete, ready-to-use Plotly code patterns for the Tufte-style standard in [SKILL.md](../SKILL.md).

> **All patterns assume the preamble code is already defined**: `get_layout()`, `add_created_at_annotation()`, `series_colours()`, `hex_to_rgba()`, `chart_colours`, and the `COLOUR_*` / `*_SCALE` constants. See SKILL.md for the preamble code block.
>
> Placeholders such as `category_col` and `value_col` stand for column names in the user's DataFrame `df`.

---

## 1. Bar Chart

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Chart Title"),
    showlegend=False
))

fig.add_trace(go.Bar(
    x=df['category_col'],
    y=df['value_col'],
    text=df['value_col'],
    textposition='outside',
    texttemplate='%{y:.1f}',
    cliponaxis=False,
    hovertemplate="Category: %{x}<br>Value: %{y:.1f}<extra></extra>",
))

fig.update_layout(xaxis_title="X Label", yaxis_title="Y Label")
add_created_at_annotation(fig)
fig.show()
```

**Gotcha**: For horizontal bar charts, add `fig.update_xaxes(showgrid=True)`.

---

## 2. Line Chart

```python
import pandas as pd

df['day'] = pd.to_datetime(df['day'])
df = df.sort_values(['series_col', 'day'])  # CRITICAL: sort by x within each series; sorting by series first also keeps legend order and colours stable

fig = go.Figure(layout=get_layout(
    title=dict(text="Trend Over Time"),
    xaxis_title="Date",
    yaxis_title="Value",
))

series_values = df['series_col'].unique()
colours_mapping = dict(zip(series_values, series_colours(len(series_values))))

for series in series_values:
    subset = df[df['series_col'] == series]
    fig.add_trace(go.Scatter(
        x=subset['day'],
        y=subset['value_col'],
        mode='lines+markers',
        marker=dict(size=8),
        line=dict(width=2),
        name=series,
        line_color=colours_mapping[series],
        hovertemplate="<b>" + series + "</b><br>Day: %{x}<br>Value: %{y:.1f}<extra></extra>",
    ))

add_created_at_annotation(fig)
fig.show()
```

### Event annotation (optional add-on)

```python
def annotate_event(fig, x, ymin, ymax, text_x, text="Major Event"):
    """Add a vertical line + text annotation for a significant event."""
    fig.add_shape(
        type="line",
        x0=x, x1=x,
        y0=ymin, y1=ymax,
        line=dict(color=COLOUR_MUTED, dash="dash")
    )
    fig.add_annotation(
        x=text_x,
        y=(ymin + ymax) / 2,
        text=text,
        showarrow=False,
        font=dict(size=12, color=COLOUR_MUTED),
    )
    return fig
```

---

## 3. Scatter Plot

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Scatter Plot Title"),
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=df['x_col'],
    y=df['y_col'],
    mode='markers+text',
    marker=dict(color=chart_colours[0], size=12),
    text=df['y_col'],
    textposition='top center',
    texttemplate='%{y:.1f}',
    hovertemplate="X: %{x}<br>Y: %{y:.1f}<extra></extra>",
))

fig.update_layout(xaxis_title="X Label", yaxis_title="Y Label")
fig.update_xaxes(showgrid=True)
add_created_at_annotation(fig)
fig.show()
```

---

## 4. Heatmap

```python
import numpy as np

pivot_df = df.pivot(index='row_col', columns='col_col', values='value_col')

fig = go.Figure(layout=get_layout(
    title=dict(text="Heatmap Title"),
))

fig.add_trace(go.Heatmap(
    z=pivot_df.values,
    x=pivot_df.columns,
    y=pivot_df.index,
    colorscale=SEQUENTIAL_SCALE,  # use DIVERGING_SCALE when values have a meaningful midpoint
    text=np.round(pivot_df.values, 1),
    texttemplate='%{text}',
    textfont={"size": 10},
    hoverongaps=False,
    hovertemplate='Col: %{x}<br>Row: %{y}<br>Value: %{z:.1f}<extra></extra>'
))

fig.update_layout(
    xaxis_title="Column Label",
    yaxis_title="Row Label",
    xaxis=dict(tickangle=0, side='bottom'),
    yaxis=dict(autorange='reversed')
)
add_created_at_annotation(fig)
fig.show()
```

---

## 5. Area Chart

```python
df = df.sort_values(by=['day', 'series_col'])
pivot_df = df.pivot(index='day', columns='series_col', values='value_col')

fig = go.Figure(layout=get_layout(
    title=dict(text="Area Chart Title"),
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=80),
))

colours = series_colours(len(pivot_df.columns))
for series, colour in zip(pivot_df.columns, colours):
    fig.add_trace(go.Scatter(
        x=pivot_df.index,
        y=pivot_df[series],
        name=series,
        mode='lines',
        fill='tonexty',
        line=dict(width=0.5),
        fillcolor=hex_to_rgba(colour, 0.3),
        line_color=colour,
        hovertemplate=series + "<br>Date: %{x}<br>Value: %{y:.1f}<extra></extra>"
    ))

fig.update_layout(xaxis_title="Date", yaxis_title="Value")
add_created_at_annotation(fig)
fig.show()
```

---

## 6. Stacked Bar Chart

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Stacked Bar Title"),
))

series_values = df['series_col'].unique()
for series, colour in zip(series_values, series_colours(len(series_values))):
    subset = df[df['series_col'] == series]
    fig.add_trace(go.Bar(
        x=subset['category_col'],
        y=subset['value_col'],
        name=series,
        marker_color=colour,
        hovertemplate=series + "<br>Category: %{x}<br>Value: %{y:.1f}<extra></extra>",
    ))

fig.update_layout(
    barmode='stack',
    xaxis_title="Category",
    yaxis_title="Value",
)
add_created_at_annotation(fig)
fig.show()
```

---

## 7. Bar + Line Combo

```python
from plotly.subplots import make_subplots

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.update_layout(get_layout(title=dict(text="Bar + Line Title")))

fig.add_trace(go.Bar(
    x=df['category_col'],
    y=df['bar_value'],
    name="Bar Metric",
    marker_color=chart_colours[0],
    hovertemplate="Category: %{x}<br>Bar: %{y:.1f}<extra></extra>",
), secondary_y=False)

fig.add_trace(go.Scatter(
    x=df['category_col'],
    y=df['line_value'],
    name="Line Metric",
    mode='lines+markers',
    marker=dict(size=8),
    line=dict(width=2, color=chart_colours[2]),
    hovertemplate="Category: %{x}<br>Line: %{y:.1f}<extra></extra>",
), secondary_y=True)

fig.update_xaxes(title_text="Category")
fig.update_yaxes(title_text="Bar Metric", secondary_y=False)
fig.update_yaxes(title_text="Line Metric", secondary_y=True)
add_created_at_annotation(fig)
fig.show()
```

---

## 8. Pie Chart

Use only for 5 or fewer categories.

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Pie Chart Title"),
))

fig.add_trace(go.Pie(
    labels=df['category_col'],
    values=df['value_col'],
    marker=dict(colors=series_colours(len(df))),
    texttemplate='%{label}<br>%{percent:.1%}',
    hovertemplate="%{label}: %{value:.1f} (%{percent:.1%})<extra></extra>",
))

add_created_at_annotation(fig)
fig.show()
```

---

## 9. Histogram

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Distribution Title"),
    showlegend=False,
))

fig.add_trace(go.Histogram(
    x=df['value_col'],
    marker_color=chart_colours[0],
    hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
))

fig.update_layout(
    xaxis_title="Value",
    yaxis_title="Count",
    bargap=0.05,
)
add_created_at_annotation(fig)
fig.show()
```

---

## 10. Boxplot

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Boxplot Title"),
))

categories = df['category_col'].unique()
for cat, colour in zip(categories, series_colours(len(categories))):
    subset = df[df['category_col'] == cat]
    fig.add_trace(go.Box(
        y=subset['value_col'],
        name=cat,
        marker_color=colour,
        boxmean='sd',
    ))

fig.update_layout(xaxis_title="Category", yaxis_title="Value")
add_created_at_annotation(fig)
fig.show()
```

---

## 11. Bubble Chart

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Bubble Chart Title"),
    showlegend=False,
))

fig.add_trace(go.Scatter(
    x=df['x_col'],
    y=df['y_col'],
    mode='markers',
    marker=dict(
        size=df['size_col'],
        sizemode='area',
        sizeref=2. * max(df['size_col']) / (40.**2),
        color=chart_colours[0],
        opacity=0.6,
        line=dict(width=1, color='white'),
    ),
    text=df['label_col'] if 'label_col' in df.columns else df['x_col'],
    hovertemplate="X: %{x:.1f}<br>Y: %{y:.1f}<br>Size: %{marker.size:.1f}<extra></extra>",
))

fig.update_layout(xaxis_title="X Label", yaxis_title="Y Label")
fig.update_xaxes(showgrid=True)
add_created_at_annotation(fig)
fig.show()
```

---

## 12. Violin Plot

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Violin Plot Title"),
))

categories = df['category_col'].unique()
for cat, colour in zip(categories, series_colours(len(categories))):
    subset = df[df['category_col'] == cat]
    fig.add_trace(go.Violin(
        y=subset['value_col'],
        name=cat,
        marker_color=colour,
        box_visible=True,
        meanline_visible=True,
    ))

fig.update_layout(xaxis_title="Category", yaxis_title="Value")
add_created_at_annotation(fig)
fig.show()
```

---

## 13. Funnel Chart

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Funnel Title"),
    showlegend=False,
))

fig.add_trace(go.Funnel(
    y=df['stage_col'],
    x=df['value_col'],
    texttemplate='%{value:,.0f} (%{percentInitial:.1%})',
    marker=dict(color=series_colours(len(df))),
    hovertemplate="Stage: %{y}<br>Count: %{x:,.0f}<br>% of Initial: %{percentInitial:.1%}<extra></extra>",
))

add_created_at_annotation(fig)
fig.show()
```

---

## Colour overflow

`chart_colours` has 7 colours. `series_colours(n)` cycles when `n > 7`, so two series end up sharing a colour. Before reaching for more colours, try one of:

- Highlight the one or two series that matter and draw the rest in `COLOUR_MUTED`.
- Split into small multiples (`make_subplots`) with a shared colour per panel.
- Direct-label the lines instead of using a legend.

```python
# Highlight one series, mute the rest
highlight = "Series A"
for series in df['series_col'].unique():
    colour = chart_colours[0] if series == highlight else COLOUR_MUTED
```

---

# Extended chart types

These go beyond the core set. They use the same preamble, palette and creation date annotation.

---

## 14. Waterfall Chart

Best for: bridges between a start and end value (revenue bridge, budget variance), net-change breakdowns.

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Bridge"),
    showlegend=False,
))

fig.add_trace(go.Waterfall(
    x=df['label_col'],
    y=df['value_col'],
    measure=df['measure_col'],  # 'relative', 'total', or 'absolute'
    connector=dict(line=dict(color=COLOUR_TEXT, width=1)),
    increasing=dict(marker=dict(color=COLOUR_POSITIVE)),
    decreasing=dict(marker=dict(color=COLOUR_NEGATIVE)),
    totals=dict(marker=dict(color=COLOUR_TOTAL)),
    texttemplate='%{y:,.0f}',
    textposition='outside',
    cliponaxis=False,
    hovertemplate="%{x}<br>Value: %{y:,.0f}<extra></extra>",
))

fig.update_layout(xaxis_title="", yaxis_title="Value")
add_created_at_annotation(fig)
fig.show()
```

---

## 15. Sankey Diagram

Best for: flows between states (migration, user journeys, funnel branches).

```python
import pandas as pd

# Build node list from unique sources + targets
all_labels = list(pd.concat([df['source_col'], df['target_col']]).unique())
label_to_idx = {label: i for i, label in enumerate(all_labels)}

node_colours = series_colours(len(all_labels))

fig = go.Figure(layout=get_layout(
    title=dict(text="Flow"),
))

fig.add_trace(go.Sankey(
    node=dict(
        label=all_labels,
        color=node_colours,
        pad=20,
        thickness=20,
        line=dict(color=COLOUR_TEXT, width=0.5),
    ),
    link=dict(
        source=[label_to_idx[s] for s in df['source_col']],
        target=[label_to_idx[t] for t in df['target_col']],
        value=df['value_col'],
        color=[hex_to_rgba(node_colours[label_to_idx[s]], 0.3) for s in df['source_col']],
    ),
))

add_created_at_annotation(fig)
fig.show()
```

---

## 16. Treemap

Best for: part-to-whole across a hierarchy (category → subcategory → item).

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Composition"),
    margin=dict(t=50, l=10, r=10, b=80),
))

fig.add_trace(go.Treemap(
    labels=df['label_col'],
    parents=df['parent_col'],
    values=df['value_col'],
    marker=dict(colors=series_colours(len(df))),
    branchvalues='total',
    texttemplate='<b>%{label}</b><br>%{value:,.0f}',
    hovertemplate='%{label}<br>Value: %{value:,.0f}<br>Parent: %{parent}<extra></extra>',
))

add_created_at_annotation(fig)
fig.show()
```

---

## 17. Sunburst

Best for: nested hierarchical drill-down.

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Hierarchical Breakdown"),
    margin=dict(t=50, l=10, r=10, b=80),
))

fig.add_trace(go.Sunburst(
    labels=df['label_col'],
    parents=df['parent_col'],
    values=df['value_col'],
    marker=dict(colors=series_colours(len(df))),
    branchvalues='total',
    hovertemplate='%{label}<br>Value: %{value:,.0f}<br>%{percentRoot:.1%} of total<extra></extra>',
))

add_created_at_annotation(fig)
fig.show()
```

---

## 18. Indicator / KPI Tile

Best for: single-number callouts with a change versus a reference period.

```python
fig = go.Figure(layout=get_layout(
    width=300,
    height=200,
    margin=dict(l=20, r=20, t=60, b=60),
))

fig.add_trace(go.Indicator(
    mode="number+delta",
    value=current_value,
    delta=dict(
        reference=previous_value,
        relative=True,
        valueformat=".1%",
        increasing=dict(color=COLOUR_POSITIVE),
        decreasing=dict(color=COLOUR_NEGATIVE),
    ),
    number=dict(
        valueformat=",",
        font=dict(size=48, family=FONT_FAMILY, color=COLOUR_TEXT),
    ),
    title=dict(
        text="KPI Title",
        font=dict(size=18, family=FONT_FAMILY, color=COLOUR_TEXT),
    ),
))

add_created_at_annotation(fig)
fig.show()
```

### KPI grid (multiple indicators)

```python
from plotly.subplots import make_subplots

# metrics: list of dicts with keys: title, value, previous, format, suffix
n = len(metrics)
fig = make_subplots(rows=1, cols=n, specs=[[{"type": "indicator"}] * n])

for i, m in enumerate(metrics):
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=m['value'],
        delta=dict(reference=m['previous'], relative=True, valueformat=".1%",
                   increasing=dict(color=COLOUR_POSITIVE), decreasing=dict(color=COLOUR_NEGATIVE)),
        number=dict(valueformat=m.get('format', ',.0f'), suffix=m.get('suffix', ''),
                    font=dict(size=36, family=FONT_FAMILY, color=COLOUR_TEXT)),
        title=dict(text=m['title'],
                   font=dict(size=14, family=FONT_FAMILY, color=COLOUR_TEXT)),
    ), row=1, col=i + 1)

fig.update_layout(get_layout(
    width=300 * n,
    height=200,
    margin=dict(l=20, r=20, t=60, b=60),
))
add_created_at_annotation(fig)
fig.show()
```

---

## 19. Horizontal Bar (Ranked)

Best for: top-N lists and rankings with long labels.

```python
df = df.sort_values('value_col', ascending=True)  # bottom-to-top for horizontal

fig = go.Figure(layout=get_layout(
    title=dict(text="Top Items"),
    showlegend=False,
))

fig.add_trace(go.Bar(
    x=df['value_col'],
    y=df['label_col'],
    orientation='h',
    text=df['value_col'],
    textposition='outside',
    texttemplate='%{x:,.1f}',
    cliponaxis=False,
    marker_color=chart_colours[0],
    hovertemplate="%{y}<br>Value: %{x:,.1f}<extra></extra>",
))

fig.update_layout(xaxis_title="Value", yaxis_title="")
fig.update_xaxes(showgrid=True)  # restore x-grid for horizontal bars
add_created_at_annotation(fig)
fig.show()
```

---

## 20. Dumbbell Chart

Best for: before → after comparison across items.

```python
df = df.sort_values('after_col', ascending=True)

fig = go.Figure(layout=get_layout(
    title=dict(text="Before vs After"),
))

# Connecting lines
for _, row in df.iterrows():
    fig.add_shape(
        type='line',
        x0=row['before_col'], x1=row['after_col'],
        y0=row['label_col'], y1=row['label_col'],
        line=dict(color=COLOUR_MUTED, width=2),
    )

# Before points (muted) and after points (emphasised)
fig.add_trace(go.Scatter(
    x=df['before_col'], y=df['label_col'],
    mode='markers', name='Before',
    marker=dict(color=COLOUR_MUTED, size=12),
    hovertemplate="%{y}<br>Before: %{x:.1f}<extra></extra>",
))

fig.add_trace(go.Scatter(
    x=df['after_col'], y=df['label_col'],
    mode='markers', name='After',
    marker=dict(color=chart_colours[0], size=12),
    hovertemplate="%{y}<br>After: %{x:.1f}<extra></extra>",
))

fig.update_layout(xaxis_title="Value", yaxis_title="")
fig.update_xaxes(showgrid=True)
add_created_at_annotation(fig)
fig.show()
```

---

## 21. Radar / Spider Chart

Best for: comparing a few entities across 4–8 dimensions on a common scale.

```python
fig = go.Figure(layout=get_layout(
    title=dict(text="Scorecard"),
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], gridcolor=COLOUR_GRID),
        angularaxis=dict(gridcolor=COLOUR_GRID),
        bgcolor=COLOUR_BACKGROUND,
    ),
))

if 'series_col' in df.columns:
    series_values = df['series_col'].unique()
    for series, colour in zip(series_values, series_colours(len(series_values))):
        subset = df[df['series_col'] == series]
        fig.add_trace(go.Scatterpolar(
            r=list(subset['value_col']) + [subset['value_col'].iloc[0]],  # close the shape
            theta=list(subset['dimension_col']) + [subset['dimension_col'].iloc[0]],
            fill='toself',
            fillcolor=hex_to_rgba(colour, 0.15),
            line=dict(color=colour, width=2),
            name=series,
        ))
else:
    fig.add_trace(go.Scatterpolar(
        r=list(df['value_col']) + [df['value_col'].iloc[0]],
        theta=list(df['dimension_col']) + [df['dimension_col'].iloc[0]],
        fill='toself',
        fillcolor=hex_to_rgba(chart_colours[0], 0.15),
        line=dict(color=chart_colours[0], width=2),
    ))

add_created_at_annotation(fig)
fig.show()
```

---

## 22. Cohort Retention Heatmap

Best for: cohort × period matrices (Month 0, Month 1, ..., Month N).

```python
import numpy as np

# df: pivot table with cohort as index, period (0, 1, 2, ...) as columns, retention % as values

fig = go.Figure(layout=get_layout(
    title=dict(text="Cohort Retention"),
    width=800,
    height=max(400, len(df) * 30),
))

fig.add_trace(go.Heatmap(
    z=df.values,
    x=[f"Month {c}" for c in df.columns],
    y=df.index.astype(str),
    colorscale=SEQUENTIAL_SCALE,
    text=np.round(df.values, 1),
    texttemplate='%{text:.1f}%',
    textfont={"size": 10},
    hoverongaps=False,
    hovertemplate='Cohort: %{y}<br>%{x}<br>Retention: %{z:.1f}%<extra></extra>',
    colorbar=dict(title="Retention %"),
))

fig.update_layout(
    xaxis_title="Period",
    yaxis_title="Cohort",
    yaxis=dict(autorange='reversed'),
)
add_created_at_annotation(fig)
fig.show()
```

---

## Semantic colour conventions

Beyond the default `chart_colours` cycle, use the semantic constants from the preamble when colour carries meaning:

| Constant | Meaning |
|---|---|
| `COLOUR_POSITIVE` | Growth, success, increase |
| `COLOUR_NEGATIVE` | Decline, failure, decrease |
| `COLOUR_TOTAL` | Totals and primary emphasis |
| `COLOUR_WARNING` | Approaching a threshold |
| `COLOUR_HIGHLIGHT` | Emphasis, selection |
| `COLOUR_MUTED` | Background, de-emphasised series, reference lines |

For categorical data with fixed meaning (status, tier, region), define a dict once and reuse it, so a category keeps its colour across charts:

```python
STATUS_COLOURS = {
    'active':   COLOUR_POSITIVE,
    'at_risk':  COLOUR_WARNING,
    'churned':  COLOUR_NEGATIVE,
    'unknown':  COLOUR_MUTED,
}
```

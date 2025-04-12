---
title: Index
toc: True
sql:
    summary: data/summary.csv
---

```js
import * as Plot from "npm:@observablehq/plot";
import * as d3 from "npm:d3";
```

# Executive Summary

```js
  const business_unit = view(
    Inputs.select(
        await sql`select null as business_unit union all select distinct business_unit from summary`,
        {
            unique: true,
            sort: true,
            label: "Business Unit:",
            format: (t) => t.business_unit,
            valueof: (t) => t.business_unit,
            value: null
        }
    )
  );

  const team = view(
    Inputs.select(
        await sql`select null as team union all select distinct team from summary`,
        {
            unique: true,
            sort: true,
            label: "Team :",
            format: (t) => t.team,
            valueof: (t) => t.team,
            value: null
        }
    )
  );

  const location = view(
    Inputs.select(
        await sql`select null as location union all select distinct location from summary`,
        {
            unique: true,
            sort: true,
            label: "Location :",
            format: (t) => t.location,
            valueof: (t) => t.location,
            value: null
        }
    )
  );
```

```sql id=executivetrend
SELECT
  Q1.datestamp,
  SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) as score,
  SUM(Q1.weighted_slo) / NULLIF(SUM(Q1.weight), 0) as slo,
  SUM(Q1.weighted_slo_min) / NULLIF(SUM(Q1.weight), 0) as slo_min
FROM
(
SELECT
  S.datestamp,
  S.metric_id,
  SUM(S.totalok) / SUM(S.total) * AVG(S.weight) as weighted_score,
  S.slo * AVG(S.weight) as weighted_slo,
  S.slo_min * AVG(S.weight) as weighted_slo_min,
  S.weight
FROM
  summary S
WHERE
  ( S.business_unit = ${business_unit} or ${business_unit} IS NULL ) AND
  ( S.team          = ${team}          or ${team}          IS NULL ) AND
  ( S.location      = ${location}      or ${location}      IS NULL )
GROUP BY
  S.datestamp,
  S.metric_id,
  S.slo,
  S.slo_min,
  S.weight
) Q1
GROUP BY
  Q1.datestamp
ORDER BY
  Q1.datestamp asc
```

```js
function executive_overview(data, width) {
  return Plot.plot({
    title: "Executive Overview",
    width,
    x: {
      ticks: 15,
      tickRotate: -45,
      tickFormat: (d) => new Date(d).toLocaleString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric"
      })
    },
    y: {
      grid: true,
      tickFormat: ",.1p",
      domain: [0, 1]
    },
    marks: [
      Plot.ruleY([0]),
      Plot.barY(data, {
        x: "datestamp", 
        y: "score",       
        fill: (d) => {
          if (d.score > d.slo) return "green";
          if (d.score > d.slo_min) return "gold";
          return "red";
        },
        tip: {
          format: {
            x: (d) => new Date(d).toLocaleString(undefined, {
              day: "numeric",
              month: "short",
              year: "numeric"
            }),
            y: (e) => (e * 100).toFixed(1) + '%'
          }
        }
      }),
      Plot.lineY(data, {x: "datestamp", y: "slo",  tip: false, stroke: "green"}),
      Plot.lineY(data, {x: "datestamp", y: "slo_min",   tip: false, stroke: "gold"}),
      Plot.text(data, {
        x: "datestamp", 
        y: "score", 
        text: (d) => (d.score * 100).toFixed(1) + '%', 
        textAnchor: "middle", 
        dx: 0,
        dy: -10,
        fontSize: 15
      }),
    ]
  });
}
```

<div class="grid grid-cols-1 gap-4" style="grid-auto-rows: auto;">
  <div class="card">${executive_overview(executivetrend,width)}</div>
</div>

---
aliases:
  - "Recipe Index"
  - "Recipes"
---
# Recipes

> Open in [Obsidian](https://obsidian.md). The dynamic queries below
> require the [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
> community plugin (Settings → Community plugins → Browse → "Dataview").

## Quick navigation

- [[#By meal type]]
- [[#By cuisine]]
- [[#By dietary]]
- [[#Quick weeknights]]
- [[#All recipes]]

## By meal type

### Dinner

```dataview
LIST
FROM "dinner"
SORT file.name ASC
```

### Breakfast

```dataview
LIST
FROM "breakfast"
SORT file.name ASC
```

### Lunch

```dataview
LIST
FROM "lunch"
SORT file.name ASC
```

### Sides

```dataview
LIST
FROM "sides"
SORT file.name ASC
```

### Desserts

```dataview
LIST
FROM "desserts"
SORT file.name ASC
```

### Appetizers

```dataview
LIST
FROM "appetizers"
SORT file.name ASC
```

### Basics (sauces, doughs, components)

```dataview
LIST
FROM "basics"
SORT file.name ASC
```

## By cuisine

```dataview
TABLE WITHOUT ID file.link AS "Recipe", cuisine
FROM "dinner" OR "lunch" OR "breakfast" OR "sides" OR "desserts" OR "appetizers" OR "basics"
WHERE cuisine != null AND cuisine != "null"
SORT cuisine ASC, file.name ASC
```

## By dietary

### Vegetarian

```dataview
LIST
FROM "dinner" OR "lunch" OR "breakfast" OR "sides" OR "desserts" OR "appetizers" OR "basics"
WHERE contains(dietary, "vegetarian")
SORT file.name ASC
```

### Vegan

```dataview
LIST
FROM "dinner" OR "lunch" OR "breakfast" OR "sides" OR "desserts" OR "appetizers" OR "basics"
WHERE contains(dietary, "vegan")
SORT file.name ASC
```

## Quick weeknights

Recipes that take 30 minutes or less.

```dataview
TABLE WITHOUT ID file.link AS "Recipe", cooking-time AS "Time", difficulty
FROM "dinner" OR "lunch" OR "basics"
WHERE cooking-time-minutes <= 30
SORT cooking-time-minutes ASC, file.name ASC
```

## Missing data

Files lacking a `meal-type` value — review and tag, or move out of `basics/`.

```dataview
LIST
FROM "basics"
WHERE meal-type = null
SORT file.name ASC
```

## All recipes

```dataview
TABLE WITHOUT ID file.link AS "Recipe", meal-type AS "Type", cuisine, cooking-time AS "Time"
FROM "dinner" OR "lunch" OR "breakfast" OR "sides" OR "desserts" OR "appetizers" OR "basics"
SORT file.name ASC
```

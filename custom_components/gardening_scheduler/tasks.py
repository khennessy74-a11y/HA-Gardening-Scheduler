"""Curated starter task catalogue with hemisphere and climate windows."""
from __future__ import annotations

# Month windows are intentionally broad. Forecast, local exposure and plant variety
# should always override these general reminders.
TASKS = [
    {"id":"general_check","title":"Check the garden after changing weather","category":"general","months":list(range(1,13)),"climates":["all"],"advice":"Look for wind damage, waterlogging, dry containers and loose supports."},
    {"id":"winter_prune_apples","title":"Prune established apple and pear trees","category":"fruit_trees","months":[1,2],"climates":["oceanic","continental","cold"],"advice":"Prune during dormancy on a dry day; avoid pruning stone fruit in winter."},
    {"id":"plant_bare_root","title":"Plant bare-root trees and shrubs","category":"fruit_trees","months":[11,12,1,2,3],"climates":["oceanic","continental","cold"],"advice":"Plant only when soil is workable and not frozen or waterlogged."},
    {"id":"start_tomatoes","title":"Start tomatoes under cover","category":"seeds_seedlings","months":[2,3,4],"climates":["oceanic","continental","mediterranean","subtropical"],"advice":"Provide bright light and warmth; delay outdoor planting until frost risk has passed."},
    {"id":"harden_seedlings","title":"Harden off seedlings","category":"seeds_seedlings","months":[3,4,5,6],"climates":["all"],"advice":"Acclimatise gradually over 7–14 days and bring tender plants in during cold or windy weather."},
    {"id":"sow_salad","title":"Sow quick-growing salad crops","category":"vegetables","months":[3,4,5,6,7,8,9],"climates":["all"],"advice":"Sow little and often; protect from heat or cold as appropriate."},
    {"id":"plant_potatoes","title":"Plant potatoes when soil is workable","category":"vegetables","months":[3,4,5],"climates":["oceanic","continental","cold"],"advice":"Avoid cold, waterlogged soil and protect emerging shoots from frost."},
    {"id":"mulch_beds","title":"Mulch beds and borders","category":"general","months":[3,4,10,11],"climates":["all"],"advice":"Mulch moist soil, leaving a gap around stems and trunks."},
    {"id":"feed_roses","title":"Feed established roses","category":"flowers_bulbs","months":[3,4,5],"climates":["all"],"advice":"Follow the product label and avoid feeding drought-stressed plants."},
    {"id":"summer_water","title":"Check containers and newly planted areas for water","category":"general","months":[5,6,7,8,9],"climates":["all"],"advice":"Water deeply when needed, preferably early or late in the day."},
    {"id":"prune_hedges","title":"Check hedges for nesting birds before trimming","category":"shrubs_hedges","months":[3,4,5,6,7,8],"climates":["all"],"advice":"Inspect carefully and follow local wildlife protection rules before any trimming."},
    {"id":"lawn_mow","title":"Check lawn growth and mowing height","category":"lawn","months":[4,5,6,7,8,9,10],"climates":["all"],"advice":"Avoid cutting too short, especially during heat or drought."},
    {"id":"autumn_bulbs","title":"Plant spring-flowering bulbs","category":"flowers_bulbs","months":[9,10,11],"climates":["oceanic","continental","mediterranean","cold"],"advice":"Choose a well-drained spot and plant at the depth recommended for the bulb."},
    {"id":"collect_leaves","title":"Clear leaves from paths and check drains","category":"general","months":[10,11,12],"climates":["all"],"advice":"Leave some leaves in suitable wildlife areas, but keep drains and paths clear."},
    {"id":"protect_tender","title":"Prepare protection for tender plants","category":"houseplants","months":[9,10,11],"climates":["all"],"advice":"Move vulnerable pots under cover before cold nights; inspect plants for pests."},
    {"id":"winter_lawn","title":"Reduce lawn traffic during wet or frosty weather","category":"lawn","months":[11,12,1,2],"climates":["all"],"advice":"Walking on saturated or frozen grass can damage the lawn."},
    {"id":"citrus_feed","title":"Review feeding and watering for citrus and tender plants","category":"houseplants","months":[3,4,5,6,7,8],"climates":["all"],"advice":"Adjust care to growth, light and the plant's specific requirements."},
    {"id":"berry_prune","title":"Review pruning needs for fruit bushes","category":"fruit_bushes","months":[1,2,3],"climates":["oceanic","continental","cold"],"advice":"Pruning varies by species; check whether your bush fruits on old or new wood."},
]

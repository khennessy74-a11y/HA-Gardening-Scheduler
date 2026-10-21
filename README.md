# Home Assistant Gardening Scheduler

A location-aware gardening task scheduler for Home Assistant. It aims to make seasonal garden care approachable for beginners while allowing experienced gardeners to configure categories and task reminders.

## Current status

Early development. This repository is not yet a validated HACS release. Do not install it on a production Home Assistant instance yet.

## Design goals

- Location-first setup: country, locality/postcode, and hemisphere/climate profile are selected during onboarding.
- Regional seasonal guidance across countries, not Ireland-only dates.
- Forecast-aware frost advice using the configured Home Assistant weather entity.
- Individually configurable task categories, with persistent complete/snooze actions.
- Sensors suitable for a dashboard and notification service support.
- No changes to existing automations, helpers, or dashboards during setup.

## Development

Integration domain: `gardening_scheduler`

The first release will use curated regional task windows and the configured weather provider. Location text is saved as context; the integration does not send it to a third-party geocoding service. Seasonal dates are guidance, not a guarantee—microclimates, soil, exposure, and plant variety matter.

## Planned validation before release

- Python syntax and Home Assistant integration tests
- Config/options flow tests
- Forecast provider variations and missing data
- HACS validation
- Manual test on a disposable Home Assistant instance
- Documentation and release tag

## Install (when a release is ready)

Add this repository as a custom repository in HACS under **Integration**, then install Gardening Scheduler and restart Home Assistant. Until a validated release is published, installation is not recommended.

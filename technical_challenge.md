# Data Engineer and Analytics Engineer Technical Challenge


## Data Engineer Challenge: Build an ETL

### Some Data

The Lingokids App generates events that are sent to our API for us to understand how our users behave. In this exercise we are interested in a particular type of event called `activity_exit`. This event is triggered when a user (parent or child) exits one of our activities, either because the activity is finished or because they decided to leave.

In the `de_data_sample` folder, you will find 3 files in JSON format that are samples of the 3 datasets described below.

Here is an example of such an event, in JSON:

```json
{
  "event_id": "205f2688-0d60-4afa-9d49-2004af2ee10d",
  "name": "activity_exit",
  "occurred_at": "2021-01-31 23:01:25.295",
  "user_id": "c7b2555c-5a37-46b6-8715-9cc2378f1ee2",
  "child_id": "314874c6-929b-40cb-9ec8-9255fdf78f3a",
  "data": {
    "activity_id": "snow_game",
    "source": "launcher",
    "duration": 232.725,
    "completed": false,
    "collection_id": "lk_collection_winterexplorer",
    "loading_time": 0.887
  },
  "context": {
    "device": {
      "device_id": "129b1f02-644d-4f1d-a99a-89017d588721",
      "brand": "Apple",
      "model": "iPad7,6"
    },
    "os": {
      "name": "iOS",
      "version": "14.2"
    },
    "app": {
      "version": "7.41.0",
      "build": "4457"
    }
  }
}
```

The `data` object in the event contains fields specific to each event type. Here we can see the following fields:

- `activity_id`: the id of the activity that the user was playing
- `source`: the screen in the App from which the user started the activity
- `duration`: the amount of time the user spent playing the activity
- `completed`: whether the user finished the activity or left before it was complete
- `collection_id`: the id of the collection the activity was part of when it was played
- `loading_time`: the time it took for the activity to load once the user opened it

Our API backend also keeps track of the subscription status of all our users. For this exercise, we assume that a subscription state moves in one direction between the following states:

| State | Entered when | Description |
|-------|-------------|-------------|
| free | user registers | The user can play a limited number of activities per day |
| trial | user starts trial | The user has full access for free for a limited time |
| subscribed | user doesn't cancel at the end of trial | The user has full access and pays a monthly subscription fee |
| lapsed | user cancels subscription | The user does not have full access anymore |

Based on this, we store for each user a record similar to the following example in JSON:

```json
{
  "user_id": "9097aa48-6be9-453f-9833-9ead1c4adfa9",
  "children_ids": [
    "826d41ee-b99f-4be8-bd7d-f688a7836dd0",
    "8fe0391a-9ca7-4e70-87ea-25ebcc11211a"
  ],
  "country_code": "in",
  "registration_at": "2021-01-12 13:34:37.139000",
  "trial_start_at": "2021-01-12 13:49:37.139000",
  "trial_end_at": "2021-01-19 13:49:37.139000",
  "subscription_start_at": "2021-01-19 13:49:37.139000",
  "subscription_expire_at": "2021-02-18 13:49:37.139000"
}
```

Finally, we also maintain metadata about all the content that has ever been available in the Lingokids App. An example of activity metadata, in JSON, looks like the following:

```json
{
  "activity_id": "rainforest_game",
  "name": "Rainforest Game",
  "type": "game",
  "subtype": "hide_and_seek"
}
```

### The Challenge

Your task is to process the input raw data and generate an output that can be used to analyse some engagement metrics. In particular, with the output you will generate, we want to be able to measure:

- the number of activities played
- the time spent playing
- the most played activities, both in terms of number of times and total duration
- the completion rate of activities

On top of that:

- we want to be able to analyse data at daily, weekly, monthly and yearly granularity.
- we want to be able to slice the data by several dimensions:
  - country
  - OS of the device (type and version) and App version
  - subscription status: free, trial, subscribed, lapsed
  - activity type and collection
- we are not interested in being able to analyse every single event or the behaviour of individual users.


## Analytics Engineer: SQL Challenge

Welcome to the Lingokids Analytics Engineer SQL assessment. This challenge is designed to evaluate your ability to work with real-world app data and extract meaningful business insights.

You'll be working with sample data from Lingokids that tracks user engagement with learning activities and subscription behaviour. The dataset represents typical analytics scenarios you'd find in an analytics role.

### Tables

**ACTIVITY_EVENTS**

Tracks when users start and finish educational activities, including how long they spent and whether they completed the activity successfully.

| event_id | user_id | activity_id | event_type | created_at | duration_seconds | completed |
|----------|---------|-------------|------------|------------|------------------|-----------|
| 'evt_001' | 12345 | 'abc123' | 'activity_exit' | '2025-01-15 10:30:00' | 120 | true |
| 'evt_002' | 12345 | 'abc123' | 'activity_enter' | '2025-01-15 10:28:00' | null | null |
| 'evt_003' | 12346 | 'def456' | 'activity_exit' | '2025-01-15 11:00:00' | 85 | false |
| ... | ... | ... | ... | ... | ... | ... |

**ACTIVITIES**

Contains the catalogue of educational content with names, themes (Math, Art, etc.), and whether it's free or premium content.

| activity_id | activity_name | theme | price_tier |
|-------------|---------------|-------|------------|
| 'abc123' | 'Count with Lisa' | 'Math' | 'free' |
| 'def456' | 'Colors Song' | 'Art' | 'premium' |
| 'ghi789' | 'Story Time' | 'Reading' | 'premium' |
| ... | ... | ... | ... |

**SUBSCRIPTIONS**

Records when users purchased subscriptions, on which platform (Apple/Google), and how much they paid.

| user_id | subscription_date | platform | price_usd |
|---------|------------------|----------|-----------|
| 12345 | '2025-01-10' | 'apple' | 7.99 |
| 12346 | '2025-01-12' | 'google' | 59.99 |
| 12347 | '2025-01-14' | 'apple' | 7.99 |
| ... | ... | ... | ... |

In the `sql_data_sample` folder, you will find the 3 files in CSV format that are samples of the 3 datasets described below.

### The Challenge

1. **Activity completion rate by theme**

   Write a SQL query that shows the completion rate for each theme. Completion rate = (completed activities / total activity attempts) * 100.

2. **Premium vs Free Content engagement**

   Write a SQL query that compares average session duration between free and premium activities, showing the count of sessions and average duration for each price tier.

3. **User subscription impact**

   Write a SQL query that shows, for each platform, the average number of activities completed per user in the 7 days before vs 7 days after their subscription date. Only include users who subscribed in January 2025.

## Expectations

### For Data Engineer Challenge

We expect you to write code that loads the datasets; transforms them as necessary; produces one or several datasets that can be used to perform further analysis.

### For Analytics Engineer Challenge

We expect you to write SQL queries that analyse the provided datasets; extract meaningful business insights; demonstrate proficiency with core SQL concepts and advanced analytical functions.

You are free to use the language and libraries/frameworks that you prefer.

You can generate your output in the format you find most appropriate and can assume that we have access to modern querying/processing tools for consuming them (data warehouse, query engine, database, ...).

We expect you to:

- spend no more than 1.5 hours (DE) / 1.5 hour (AE)
- write a solution that we can easily execute on a laptop for evaluation
- include a README describing your approach and assumptions *(DE only)*
- write code/queries with the same care you would use in your job
- include some level of automated testing or data validation *(DE only)*
- explain how you would scale your solution to handle millions of daily events *(DE only)*

### Evaluation Criteria

We will evaluate all aspects of your submission, particularly:

- **Technical Proficiency**: Data processing logic (DE) / SQL skills and query correctness (AE)
- **Code Quality**: Clean, readable, maintainable code with proper structure
- **Business Understanding**: Appropriate solutions for the analytical use cases
- **Best Practices**: ETL patterns (DE) / SQL optimisation and clarity (AE)

Avoid spending all your time perfecting one aspect - we evaluate the complete solution. If your submission meets our expectations, you'll have time to discuss improvements in follow-up interviews.

If you have any questions about the challenge, don't hesitate to reach out.

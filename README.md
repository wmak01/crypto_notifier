# Crypto Notifier (Manual State Version)

This app monitors crypto prices and emails buy/sell instructions
based on percentage rules and buffers.

## How it works
1. You define your current state in `state.txt`
2. App checks price every X seconds
3. If a rule triggers:
   - Email is sent
   - App pauses (pending=true)
4. You execute trade manually
5. You update `state.txt`
6. You reset `pending.json` to false
7. App continues

Safe. Manual. Controlled.

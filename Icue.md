# iCUE iFrame Setup

CORSAIR's XENEON EDGE iFrame widget accepts full iframe HTML. CORSAIR's guide says you can paste the full iFrame code directly into the widget.

Source:
- https://www.corsair.com/ca/ru/explorer/gamer/monitors/things-you-can-do-in-icue-with-the-xeneon-edge/

## Paste this into iCUE

Use this first:

```html
<iframe
  src="https://127.0.0.1:8766/"
  title="DSS Support Tool"
  width="100%"
  height="100%"
  style="border:none; background:#0b1220;"
  referrerpolicy="no-referrer"
  allow="fullscreen">
</iframe>
```

If iCUE does not like `127.0.0.1`, try this variant:

```html
<iframe
  src="https://localhost:8766/"
  title="DSS Support Tool"
  width="100%"
  height="100%"
  style="border:none; background:#0b1220;"
  referrerpolicy="no-referrer"
  allow="fullscreen">
</iframe>
```

## How to use it

1. Start `DSS Support Tool`.
2. Open iCUE.
3. Open the `XENEON EDGE` tile.
4. Click `+` to add a widget.
5. Choose the `iFrame` widget.
6. Paste one of the iframe blocks above.
7. Save the widget.

## Important

- The app serves normal desktop traffic on `http://127.0.0.1:8765`.
- iCUE should use the HTTPS endpoint on `https://127.0.0.1:8766` or `https://localhost:8766`.
- The local certificate authority file is created here:

```text
C:\Users\<your-user>\AppData\Local\DSS Support Tool\certs\localhost-ca.pem
```

- The current build also tries to trust that CA automatically in the Windows current-user certificate store on startup.
- If iCUE still shows an SSL error, fully close and reopen iCUE after starting DSS Support Tool.
- If it still fails, try the `localhost` iframe instead of `127.0.0.1`, or the other way around.

## Quick checks

Open these in a normal browser first:

- `https://127.0.0.1:8766/api/status`
- `https://localhost:8766/api/status`

If one works and the other does not, use the one that works in the iframe snippet.

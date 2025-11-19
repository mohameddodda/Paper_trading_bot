# Security Policy

**Paper Trading Bot** takes your privacy and security seriously — even though **no real money is involved**.

—

## Supported Versions

We actively support only the **latest version** of the bot.

| Version | Supported |
|———|————|
| `main` (latest) | Yes |
| Older releases | No |

> **Always run the latest version** from [GitHub](https://github.com/mohameddodda/Paper_trading_bot)

—

## Reporting a Vulnerability

Found a security issue? **Thank you** — we want to know.

**Email**: `mohamed.hisham282@yahoo.com`  
**X (Twitter)**: [@MohamedDodda](https://x.com/MohamedDodda) (DMs open)

All reports are:
- Reviewed **within 24 hours**
- Kept **strictly confidential**
- Acknowledged with a response plan

—

## API Key Security (OpenRouter)

Your **OpenRouter API key** is:

- **Stored only on your iOS device** (via **Keychain**)
- **Never transmitted** to us or any third party
- **Never logged** or saved in plaintext
- **Never committed** to GitHub (`.env` is gitignored)

We **do not** collect:
- Usage data
- Trade logs
- Personal information

—

## Best Practices

1. **Use a free OpenRouter account**  
   → [openrouter.ai](https://openrouter.ai) gives **$5 free credit**  
   → No credit card required

2. **Never share your API key**

3. **Revoke if compromised**  
   → Go to [openrouter.ai/keys](https://openrouter.ai/keys) → Click **”Revoke”**

4. **Use `.env.example` as template**  
   ```env
   OPENROUTER_API_KEY=sk-or-your-key-here
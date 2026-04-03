# Security Policy

**Paper Trading Bot** takes your privacy and security seriously — even though **no real money is involved**. This bot is for **educational paper trading simulations only**. It does not handle real funds, trades, or financial data. Use at your own risk for learning purposes.

## Supported Versions

We actively support only the **latest version** of the bot.

Version         Supported

main (latest)   :white_check_mark: Yes

Older releases   :x: No

Always run the latest version from GitHub


Reporting a Vulnerability
Found a security issue? Thank you — we want to know.

Email: mohamed.hisham282@yahoo.com

All reports are:

Reviewed within 48 hours
Kept strictly confidential
Acknowledged with a response plan
API Key Security
Your API keys (e.g., OpenRouter, optional cloud/AWS) are handled securely:

Stored locally: On your device (via .env file, which is gitignored). On iOS, uses Keychain for extra protection.
Never transmitted: To us, third parties, or logged in plaintext.
Never committed: To GitHub—.env is in .gitignore.
Optional features: AI, cloud, and streaming require keys but disable gracefully if missing.
We do not collect:

Usage data
Trade logs
Personal information (PII)
Real financial data
Data Privacy
No data collection: The bot fetches public market data (e.g., from Yahoo Finance or Crypto.com APIs) and processes it locally.
Local storage: Logs and models are saved on your device (e.g., logs/, checkpoints/).
No sharing: Data is not sent to external servers unless you enable optional cloud features (e.g., AWS, which you control).
Compliance: Follows general data protection best practices; no GDPR/PII handling as no user data is collected.
Dependency Risks
Third-party libraries: Uses open-source packages (e.g., TensorFlow, Stable-Baselines3). Update regularly via pip install -r requirements.txt.
API limits: Respects rate limits on public APIs; no excessive requests.
Vulnerabilities: Monitor for updates in dependencies. Report issues if found.
Best Practices
Use a free OpenRouter account
→ openrouter.ai gives $5 free credit
→ No credit card required

Never share your API keys
→ Store in .env (copy from .env.example)

Revoke keys if compromised
→ OpenRouter: openrouter.ai/keys → Revoke
→ AWS/Other: Revoke via their dashboards

Run in a virtual environment
→ python -m venv venv && venv\Scripts\activate (Windows)
→ Keeps dependencies isolated

Update regularly
→ Pull latest from GitHub and run pip install -r requirements.txt

Disable optional features
→ If unsure, set USE_AI=False in config.py

Contact
For security concerns or questions:
Email: mohamed.hisham282@yahoo.com

Last updated: 2026


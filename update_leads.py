import requests
import os

# ============================================
# ✏️ EDIT THESE TWO LINES WITH YOUR TEMPLATE NAMES
PRIVATE_LABEL_TEMPLATE = "prm_plant_protein_09062026"
WHOLESALE_TEMPLATE     = "hhw_joint_care_09062026"
# ============================================

# Zoho API Credentials (from GitHub Secrets)
CLIENT_ID     = os.environ["ZOHO_CLIENT_ID"]
CLIENT_SECRET = os.environ["ZOHO_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["ZOHO_REFRESH_TOKEN"]

# ============================================
# STEP 1: Get Access Token
# ============================================
def get_access_token():
    url = "https://accounts.zoho.in/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "refresh_token"
    }
    response = requests.post(url, params=params)
    token = response.json().get("access_token")
    if not token:
        raise Exception("Failed to get access token: " + str(response.json()))
    print("✅ Access token received")
    return token

# ============================================
# STEP 2: Fetch All Leads by Industry
# ============================================
def get_leads_by_industry(token, industry_value):
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    all_leads = []
    page = 1

    while True:
        url = "https://www.zohoapis.in/crm/v2/Leads/search"
        params = {
            "criteria": f"(Industry:equals:{industry_value})",
            "per_page": 200,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "data" not in data:
            break

        leads = data["data"]
        all_leads.extend(leads)
        print(f"  📄 Page {page} → {len(leads)} leads fetched")

        if not data.get("info", {}).get("more_records"):
            break
        page += 1

    print(f"✅ Total {industry_value} leads: {len(all_leads)}")
    return all_leads

# ============================================
# STEP 3: Update Leads in Batches of 100
# ============================================
def update_leads(token, leads, template_name):
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type": "application/json"
    }
    url = "https://www.zohoapis.in/crm/v2/Leads"

    # Split into batches of 100
    batch_size = 100
    total_updated = 0

    for i in range(0, len(leads), batch_size):
        batch = leads[i:i + batch_size]

        payload = {
            "data": [
                {
                    "id": lead["id"],
                    "RM_Template_Name": template_name
                }
                for lead in batch
            ]
        }

        response = requests.put(url, headers=headers, json=payload)
        result = response.json()

        success = sum(1 for r in result.get("data", []) if r.get("code") == "SUCCESS")
        total_updated += success
        print(f"  ✅ Batch {i//batch_size + 1} → {success}/{len(batch)} updated")

    print(f"✅ Total updated: {total_updated} leads")
    return total_updated

# ============================================
# MAIN RUN
# ============================================
def main():
    print("\n🚀 Starting Zoho CRM Lead Update...")
    print("=" * 45)

    # Get token
    token = get_access_token()

    # --- Private Label Leads ---
    print("\n📦 Processing Private Label leads...")
    pl_leads = get_leads_by_industry(token, "Private Label")
    if pl_leads:
        update_leads(token, pl_leads, PRIVATE_LABEL_TEMPLATE)
    else:
        print("⚠️ No Private Label leads found")

    # --- Wholesale Leads ---
    print("\n🏪 Processing Wholesale leads...")
    ws_leads = get_leads_by_industry(token, "Wholesale")
    if ws_leads:
        update_leads(token, ws_leads, WHOLESALE_TEMPLATE)
    else:
        print("⚠️ No Wholesale leads found")

    print("\n✅ All done! Zoho CRM leads updated successfully.")
    print("=" * 45)

if __name__ == "__main__":
    main()

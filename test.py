import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def get_team_roster_urls(league_url, season_label):
    resp = requests.get(league_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    base_url = "https://www.eliteprospects.com"
    roster_urls = []

    # Find the heading <h2> with text "WHL Team Rosters"
    heading = soup.find("h2", string="NHL Team Rosters")
    if not heading:
        print("❌ 'WHL Team Rosters' heading not found")
        return []

    # Find the div with id="league-team-rosters" after the heading
    roster_div = heading.find_next("div", id="league-team-rosters")
    if not roster_div:
        print("❌ 'league-team-rosters' div not found")
        return []

    # Find the <ul> containing the teams
    teams_list = roster_div.find("ul", class_="TeamRoster_teamRoster__y6g5I")
    if not teams_list:
        print("❌ Teams list <ul> not found")
        return []

    # Extract team URLs from the <a> tags inside the <li>s
    for li in teams_list.find_all("li"):
        a_tag = li.find("a", href=True)
        if a_tag:
            href = a_tag['href']
            team_base_url = base_url + href.split("?")[0]
            full_roster_url = f"{team_base_url}/{season_label}#players"
            if full_roster_url not in roster_urls:
                roster_urls.append(full_roster_url)

    return roster_urls

# Example usage:
league_url = "https://www.eliteprospects.com/league/nhl/2023-2024"
season = "2023-2024"
roster_urls = get_team_roster_urls(league_url, season)

print(f"Found {len(roster_urls)} team roster URLs:")
for url in roster_urls:
    print(url)

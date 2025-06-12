from sheet_makers.qb_sheet import make_qb_sheet
from sheet_makers.wr_sheet import make_wr_sheet
from sheet_makers.team_sheet import make_team_sheet, make_opp_stats
from sheet_makers.rb_sheet import make_rb_sheet
from utils.helpers import get_output_path
import pandas as pd 

def main():
    opp_stats = make_opp_stats()
    df_qb = make_qb_sheet(opp_stats)
    df_team = make_team_sheet(opp_stats)
    df_wr = make_wr_sheet(opp_stats)
    df_rb = make_rb_sheet(opp_stats)

    output_file_path = get_output_path('nfl_stats_2024.xlsx')

    with pd.ExcelWriter(output_file_path, engine="xlsxwriter") as writer:
        #write each df to a different tab
        df_team.to_excel(writer, sheet_name="Team Stats", index=False)
        df_qb.to_excel(writer, sheet_name="QB Stats", index=False)
        df_wr.to_excel(writer, sheet_name="WR TE Stats", index=False)
        df_rb.to_excel(writer, sheet_name="RB Stats", index=False)
    print(f"Excel file successfully saved at: {output_file_path}")

    # Save HTML
    html_output_path = get_output_path('nfl_stats_2024.html')
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write("<html><head><title>NFL Stats</title></head><body>")
        f.write("<h1>NFL Stats 2024</h1>")

        f.write("<h2>Team Stats</h2>")
        f.write(df_team.to_html(index=False))

        f.write("<h2>QB Stats</h2>")
        f.write(df_qb.to_html(index=False))

        f.write("<h2>WR/TE Stats</h2>")
        f.write(df_wr.to_html(index=False))

        f.write("<h2>RB Stats</h2>")
        f.write(df_rb.to_html(index=False))

        f.write("</body></html>")

    print(f"HTML file successfully saved at: {html_output_path}")


if __name__ == "__main__":
   main()
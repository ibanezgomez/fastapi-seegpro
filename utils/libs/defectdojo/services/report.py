class DojoReport:
    def get_report_by_test(self, test_id, include_executive_summary=True, include_disclaimer=True):
        report_type = "HTML"
        
        executive_summary = "0"
        if include_executive_summary: executive_summary = "1"

        disclaimer = "0"
        if include_executive_summary: disclaimer = "1"

        path = f"/test/{str(test_id)}/report?include_executive_summary={executive_summary}&report_type={report_type}&include_disclaimer={disclaimer}&_generate="
        url = self.server + path

        res = self.session.get(url)
        if res and res.status_code == 200:
            return res.text
        else:
            return None
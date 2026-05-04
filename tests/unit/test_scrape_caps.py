from scripts.scrape_caps import CapsDocument, infer_phase, normalize_url, parse_caps_documents, slugify


def test_slugify_normalizes_caps_titles():
    assert slugify("Mathematics Grades R-3 (English)") == "mathematics-grades-r-3-english"


def test_caps_document_filename_uses_nearby_title_for_linkclick():
    doc = CapsDocument(
        title="Mathematics English",
        url="https://www.education.gov.za/LinkClick.aspx?fileticket=abc%3D&portalid=0",
        source_page="https://www.education.gov.za/CAPSFoundation",
    )

    assert doc.filename == "mathematics-english.pdf"


def test_parse_caps_documents_keeps_only_dbe_pdf_links():
    html = """
    <table>
      <tr>
        <td>Mathematics English</td>
        <td><a href="/LinkClick.aspx?fileticket=abc%3D&portalid=0">Download</a></td>
      </tr>
      <tr>
        <td>External</td>
        <td><a href="https://example.com/file.pdf">Download</a></td>
      </tr>
    </table>
    """

    docs = parse_caps_documents(
        html,
        "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements/CAPSFoundation/tabid/571/Default.aspx",
    )

    assert len(docs) == 1
    assert docs[0].title == "Mathematics English"
    assert docs[0].phase == "grades-r-3"
    assert docs[0].language == "english"
    assert docs[0].subject == "mathematics"


def test_infer_phase_from_grade_text():
    assert infer_phase("https://www.education.gov.za/caps", "Natural Sciences Grades 7-9") == "grades-7-9"


def test_normalize_url_deduplicates_forcedownload_links():
    url = normalize_url(
        "/LinkClick.aspx?fileticket=abc%3D&tabid=571&forcedownload=true",
        "https://www.education.gov.za/CAPSFoundation",
    )

    assert url == "https://www.education.gov.za/LinkClick.aspx?fileticket=abc%3D&tabid=571"

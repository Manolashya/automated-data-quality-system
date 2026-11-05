
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


# Locate the project directories.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEMPLATE_DIR = (
    PROJECT_ROOT / "src" / "reporting" / "templates"
)

TEMPLATE_NAME = "report_template.html"

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"


def generate_html_report(
    profiling_report,
    validation_issues=None,
    output_path=None,
):
    """
    Generate an HTML data quality report.

    Args:
        profiling_report: Dictionary returned by profile_dataframe().
        validation_issues: List of validation issue dictionaries.
        output_path: Optional custom path for the HTML report.

    Returns:
        Path to the generated HTML report.

    Raises:
        TypeError: If the profiling report is not a dictionary.
        ValueError: If the profiling report is empty.
        FileNotFoundError: If the HTML template is missing.
    """

    # Validate profiling report.
    if not isinstance(profiling_report, dict):
        raise TypeError(
            "profiling_report must be a dictionary."
        )

    if not profiling_report:
        raise ValueError(
            "profiling_report cannot be empty."
        )

    # Use an empty list when no validation issues are supplied.
    if validation_issues is None:
        validation_issues = []

    if not isinstance(validation_issues, list):
        raise TypeError(
            "validation_issues must be a list."
        )

    # Configure Jinja2 with HTML autoescaping.
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm"),
            default_for_string=True,
        ),
    )

    # Load the HTML template.
    template = environment.get_template(TEMPLATE_NAME)

    # Render the HTML report.
    html_content = template.render(
        report=profiling_report,
        validation_issues=validation_issues,
    )

    # Determine the output location.
    if output_path is None:
        file_name = profiling_report.get(
            "file_name",
            "dataset.csv",
        )

        output_file = (
            DEFAULT_OUTPUT_DIR
            / f"{Path(str(file_name)).stem}_report.html"
        )

    else:
        output_file = Path(output_path)

        if not output_file.is_absolute():
            output_file = PROJECT_ROOT / output_file

    # Create the output directory if necessary.
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save the HTML report.
    output_file.write_text(
        html_content,
        encoding="utf-8",
    )

    return output_file

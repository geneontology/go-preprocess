"""Module contains the CLI commands for the gopreprocess package."""

import click
from gopreprocess.goa_annotation_creation_controller import P2GAnnotationCreationController
from gopreprocess.ortho_annotation_creation_controller import AnnotationCreationController

from src.gopreprocess.file_processors.gpad_processor import GpadProcessor
from src.utils.decorators import timer
from src.utils.differ import compare_files
from src.utils.download import download_file, download_files
from src.utils.generate_gpad import generate_gpad_file
from src.utils.merge_gafs import merge_files_from_directory


# Create a group for the CLI commands
@click.group()
@timer
def cli():
    """A CLI for preprocessing GO annotations."""
    pass


@cli.command(name="convert_annotations")
@click.option(
    "--namespaces",
    default=["RGD", "UniProtKB"],
    help="List of providers in the source GAF that should be "
    "used to retrieve source annotations for conversion. "
    "e.g. [RGD, HGNC, UniProtKB]",
)
@click.option(
    "--target_taxon",
    default="NCBITaxon:10090",
    help="Target taxon in curie format using NCBITaxon prefix., e.g. NCBITaxon:10090",
)
@click.option(
    "--source_taxon",
    default="NCBITaxon:10116",
    help="Source taxon in curie format using NCBITaxon prefix, e.g. NCBITaxon:10116",
)
@click.option(
    "--ortho_reference", default="GO_REF:0000096", help="Ortho reference in curie format, e.g. GO_REF:0000096"
)
def convert_annotations(namespaces, target_taxon, source_taxon, ortho_reference):
    """Converts annotations from one taxon to another using orthology."""
    print("namespaces: ", namespaces)
    print("target_taxon: ", target_taxon)
    print("source_taxon: ", source_taxon)
    print("ortho_reference: ", ortho_reference)
    converter = AnnotationCreationController(namespaces, target_taxon, source_taxon, ortho_reference)
    converter.convert_annotations()


@cli.command(name="compare")
@click.option("--file1", "-file1", type=click.Path(), required=True, help="file1 is the source file.")
@click.option(
    "--file2",
    "-file2",
    type=click.Path(),
    required=True,
    help="file2 is the file that is the result of a transformation, or the target file.",
)
@click.option(
    "--output",
    "-o",
    type=click.STRING,
    required=True,
    default=["Evidence_code"],
    help="the name of the prefix for all files generated by this tool.",
)
def compare(file1, file2, output):
    """
    Compare two GPAD or GAF files and report differences.

    <file1>: Name of the source file to compare.
    <file2>: Name of the target/second file to compare.

    Options:
      --output <output>: Prefix for output files/reports. (Default: comparison)
      --group-by-column <column>: Columns to group the comparison. (Multiple values allowed)
      --restrict-to-decreases: Restrict to decreases only.
    """
    print("file1: ", file1)
    print("file2: ", file2)
    print("output: ", output)
    compare_files(file1, file2, output)


@cli.command(name="download")
@click.option("--source_taxon", "-source_taxon", type=str, required=True, help="Source taxon in curie format.")
@click.option(
    "--target_taxon",
    "-target_taxon",
    type=str,
    required=True,
    help="Target taxon in curie format.",
)
def download(source_taxon, target_taxon):
    """
    Compare two GPAD or GAF files and report differences.

    <file1>: Name of the source file to compare.
    <file2>: Name of the target/second file to compare.

    Options:
      --output <output>: Prefix for output files/reports. (Default: comparison)
      --group-by-column <column>: Columns to group the comparison. (Multiple values allowed)
      --restrict-to-decreases: Restrict to decreases only.
    """
    print("source_taxon: ", source_taxon)
    print("target_taxon: ", target_taxon)
    download_files(source_taxon, target_taxon)
    download_file("MGI_GPI", "MGI_GPI", gunzip=True)


@click.command()
def merge_files():
    """Merge all GAF files from a directory into one output file."""
    resulting_file = merge_files_from_directory("GAF_OUTPUT")
    print("merged file path", resulting_file)


@click.command()
def get_gpad_file():
    """Merge all GAF files from a directory into one output file."""
    resulting_file = generate_gpad_file()
    print("gpad file path", resulting_file)


@cli.command(name="convert_g2p_annotations")
@click.option("--source_taxon", "-source_taxon", type=str, required=True, help="Source taxon in curie format.")
@click.option(
    "--isoform",
    "-isoform",
    type=bool,
    required=True,
    help="Whether or not to process an isoform file as well.",
)
def convert_p2g_annotations(isoform: bool, source_taxon: str):
    """
    Converts annotations from one taxon to another using orthology.

    :param isoform: Whether to process isoform annotations.
    :type isoform: bool
    :param source_taxon: The source taxon in curie format.
    :type source_taxon: str
    """
    converter = P2GAnnotationCreationController()
    converter.convert_annotations(isoform=isoform, taxon=source_taxon)


@cli.command(name="convert_noctua_gpad_1_2_to_2_0_annotations")
def convert_noctua_gpad_1_2_to_2_0_annotations():
    """Converts annotations from one GPAD format 1.2 as output from noctua to another using ontobio functions."""
    noctua_gpad = download_file(target_directory_name="MGI_NOCTUA", config_key="MGI_NOCTUA", gunzip=True)
    gpp = GpadProcessor(noctua_gpad)
    new_noctua_gpad_filepath = gpp.convert_noctua_gpad()
    print("new noctua gpad filepath: ", new_noctua_gpad_filepath)
    return new_noctua_gpad_filepath


if __name__ == "__main__":
    """
    Execute the CLI commands via this entrypoint.

    """
    cli()

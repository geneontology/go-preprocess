import click
from src.utils.differ import compare_files
from src.gopreprocess.converters.annotation_converter import AnnotationConverter
from src.utils.decorators import convert_to_list


# Create a group for the CLI commands
@click.group()
def cli():
    pass


@cli.command(name="convert_annotations")
@click.option("--namespaces", default=["RGD", "UniProtKB"], help="List of providers in the source GAF that should be "
                                                                 "used to retrieve source annotations for conversion. "
                                                                 "e.g. [RGD, HGNC, UniProtKB]")
@click.option("--target_taxon", default="NCBITaxon:10090", help="Target taxon in curie format using NCBITaxon prefix. "
                                                                "e.g. NCBITaxon:10090")
@click.option("--source_taxon", default="NCBITaxon:10116", help="Source taxon in curie format using NCBITaxon prefix. "
                                                                "e.g. NCBITaxon:10116")
@click.option("--ortho_reference", default="GO_REF:0000096", help="Ortho reference in curie format. "
                                                                  "e.g. GO_REF:0000096")
def convert_annotations(namespaces, target_taxon, source_taxon, ortho_reference):
    print("namespaces: ", namespaces)
    print("target_taxon: ", target_taxon)
    print("source_taxon: ", source_taxon)
    print("ortho_reference: ", ortho_reference)
    converter = AnnotationConverter(namespaces, target_taxon, source_taxon, ortho_reference)
    converter.convert_annotations()


@cli.command(name="compare")
@click.option("--file1",
              "-file1",
              type=click.Path(),
              required=True,
              help='file1 is the source file.')
@click.option("--file2",
              "-file2",
              type=click.Path(),
              required=True,
              help='file2 is the file that is the result of a transformation, or the target file.')
@click.option("--output",
              "-o",
              type=click.STRING,
              required=True,
              default=["Evidence_code"],
              help='the name of the prefix for all files generated by this tool.')
@click.option("--group_by_columns",
              "-gb",
              required=False,
              type=str, callback=convert_to_list,
              help='GAF or GPAD columns to group by including: subject, relation, object, negated')
def compare(file1, file2, output, group_by_columns):
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
    print("group_by_column: ", group_by_columns, type(group_by_columns))
    compare_files(file1, file2, output, group_by_columns)


if __name__ == '__main__':
    cli()


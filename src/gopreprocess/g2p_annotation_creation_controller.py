"""
This module contains the Protein 2 GO AnnotationConverter class.
"""
from src.gopreprocess.file_processors.gafprocessor import GafProcessor
from src.utils.decorators import timer
from src.utils.download import concatenate_gafs, download_file, download_files
from src.gopreprocess.file_processors.gpiprocessor import GpiProcessor
from ontobio.model.association import Curie, GoAssociation, ConjunctiveSet
import copy
import pystow
import datetime


def generate_annotation(annotation: GoAssociation, xrefs: dict) -> GoAssociation:
    """
    Generate a new annotation based on the given protein 2 GO annotation.

    :param annotation: The protein 2 GO annotation.
    :type annotation: GoAssociation
    :param xrefs: The xrefs dictionary from the parsed GPI file, mapping the gene of the target
    species to the set of UniProt ids for the source - in this case, the source is the protein 2 GO GAF file,
    so really we're still dealing with the source taxon.

    :return: A new annotation.
    :rtype: GoAssociation)
    """
    if str(annotation.subject.id) in xrefs.keys():
        new_gene = Curie(namespace="MGI",
                         identity=xrefs[str(annotation.subject.id)].replace("MGI:MGI:", "MGI:"))
        print(new_gene.identity)
        new_annotation = copy.deepcopy(annotation)
        # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
        new_annotation.subject.id = new_gene
        new_annotation.subject.synonyms = []
        new_annotation.object.taxon = Curie.from_str("NCBITaxon:10090")
        new_annotation.provided_by = "GO_Central"
        return new_annotation
    else:
        return None


class P2GAnnotationCreationController:

    """
    Converts annotations from one species to another based on ortholog relationships between the two species.

    """

    def __init__(self):
        """
        Initialize the AnnotationConverter class.

        """

    @timer
    def convert_annotations(self) -> None:
        """
        Convert Protein to GO annotations from source to target taxon.

        :returns: None
        """
        converted_target_annotations = []

        p2go_file = download_file(target_directory_name="GOA_MOUSE", config_key="GOA_MOUSE", gunzip=True)
        target_gpi_path = download_file(target_directory_name="MGI_GPI", config_key="MGI_GPI", gunzip=True)

        gpi_processor = GpiProcessor(target_gpi_path)
        xrefs = gpi_processor.get_xrefs()

        # assign the output of processing the source GAF to a source_annotations variable
        gp = GafProcessor(filepath=p2go_file)
        source_annotations = gp.parse_p2g_gaf()

        for annotation in source_annotations:
            new_annotation = generate_annotation(
                    annotation=annotation,
                    xrefs=xrefs
            )
            if new_annotation is not None:
                converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        header_filepath = pystow.join(
            key="GAF_OUTPUT",
            name="mgi-p2g-converted.gaf",
            ensure_exists=True,
        )

        # here's the final write to the final file
        with open(header_filepath, "w") as file:
            file.write("!gaf-version: 2.2\n")
            file.write("!Generated by: GO_Central preprocess pipeline: protein to GO transformation\n")
            file.write("!Date Generated: " + str(datetime.date.today()) + "\n")
            for annotation in converted_target_annotations:
                file.write('\t'.join(map(str, annotation)) + '\n')

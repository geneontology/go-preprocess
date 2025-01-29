"""combine and convert gpad to gpad2.0."""

import datetime
from pathlib import Path

import pystow
from ontobio.io.gpadparser import GpadParser

from utils.decorators import timer


class GpadProcessor:

    """
    A class for processing GPAD files.

    :param filepath: The path to the GPAD file.
    :type filepath: str
    """

    def __init__(self, filepath: Path):
        """
        Initializes a new instance of GpiProcessor.

        :param filepath: The path to the GPI file.
        :type filepath: str
        """
        self.gpad_filepath: Path = filepath

    @timer
    def convert_noctua_gpad(self) -> Path:
        """
        Parses the GPAD file and extracts the annotations, remaking them as gpad2.0.

        :return: A filepath to the recreated GPAD file.
        """
        p = GpadParser()
        new_associations = []
        with open(self.gpad_filepath, "r") as file:
            for line in file:
                annotation = p.parse_line(line)
                for source_assoc in annotation.associations:
                    if isinstance(source_assoc, dict):
                        continue  # skip the header
                    else:
                        gpad2_0_association = source_assoc.to_gpad_2_0_tsv()
                        new_associations.append(gpad2_0_association)
        new_gpad_filepath = self.dump_annotations(new_associations)
        return new_gpad_filepath

    def dump_annotations(self, annotations: []):
        """Dump annotations to a file."""
        file_suffix = self.gpad_filepath.stem.split("_")[0]
        header_filepath = pystow.join(
            key="GPAD_2_OUTPUT",
            name=f"mgi_noctua_2_0_{file_suffix}.gpad",
            ensure_exists=True,
        )

        with open(header_filepath, "w") as file:
            file.write("!gpa-version: 2.0\n")
            file.write("!Generated by: GO_Central preprocess pipeline: noctua GPAD transformation\n")
            file.write("!Date Generated: " + str(datetime.date.today()) + "\n")
            for annotation in annotations:
                file.write("\t".join(map(str, annotation)) + "\n")

        return header_filepath

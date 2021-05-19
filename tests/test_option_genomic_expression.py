from uuid import uuid4
from phc.easy.omics.options.genomic_expression import GenomicExpressionOptions

variant_set_ids = [str(uuid4())]


def test_genomic_expression_option():
    result = GenomicExpressionOptions(
        variant_set_ids=variant_set_ids, expression="1-2"
    ).dict()
    assert result.get("expression") == "1-2"

    result = GenomicExpressionOptions(
        variant_set_ids=variant_set_ids, expression=">= 1.2"
    ).dict()
    assert result.get("expression") == "1.2:gte"

    result = GenomicExpressionOptions(
        variant_set_ids=variant_set_ids, expression="<=1.2"
    ).dict()
    assert result.get("expression") == "1.2:lte"

    result = GenomicExpressionOptions(
        variant_set_ids=variant_set_ids, expression="1.2:lte"
    ).dict()
    assert result.get("expression") == "1.2:lte"

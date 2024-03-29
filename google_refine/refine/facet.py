"""
OpenRefine Facets, Engine, and Facet Responses.
"""

import json
import re


def to_camel(attr):
    """convert this_attr_name to thisAttrName."""
    # Do lower case first letter
    return attr[0].lower() + re.sub(r'_(.)', lambda x: x.group(1).upper(), attr[1:])


def from_camel(attr):
    """convert thisAttrName to this_attr_name."""
    # Don't add an underscore for capitalized first letter
    return re.sub(r'(?<=.)([A-Z])', lambda x: '_' + x.group(1), attr).lower()


class Facet:
    def __init__(self, column, facet_type, **options):
        self.name = column
        self.column_name = column
        self.type = facet_type
        for k, v in options.items():
            setattr(self, k, v)

    def as_dict(self):
        return {
            to_camel(k): v
            for k, v in self.__dict__.items()
            if v is not None
        }


class TextFilterFacet(Facet):
    def __init__(self, column, query, **options):
        super().__init__(
            column,
            facet_type='text',
            query=query,
            case_sensitive=False,
            mode='text',
            **options,
        )


class TextFacet(Facet):
    def __init__(
            self, column,
            selection=None,
            expression='value',
            omit_blank=False,
            omit_error=False,
            select_blank=False,
            select_error=False,
            invert=False,
            **options,
    ):
        super().__init__(
            column,
            facet_type='list',
            omit_blank=omit_blank,
            omit_error=omit_error,
            select_blank=select_blank,
            select_error=select_error,
            invert=invert,
            **options,
        )
        self.expression = expression
        self.selection = []

        if selection is None:
            selection = []
        elif not isinstance(selection, list):
            selection = [selection]
        for value in selection:
            self.include(value)

    def include(self, value):
        for s in self.selection:
            if s['v']['v'] == value:
                return
        self.selection.append({'v': {'v': value, 'l': value}})
        return self

    def exclude(self, value):
        self.selection = [
            s
            for s in self.selection
            if s['v']['v'] != value
        ]
        return self

    def reset(self):
        self.selection = []
        return self


class BoolFacet(TextFacet):
    def __init__(self, column, expression, selection=None):
        if selection is not None and not isinstance(selection, bool):
            raise ValueError('selection must be True or False.')
        if expression is None:
            raise ValueError('Missing expression')
        super().__init__(
            column,
            expression=expression,
            selection=[selection],
        )


class StarredFacet(BoolFacet):
    def __init__(self, selection=None):
        super().__init__('', expression='row.starred', selection=selection)


class FlaggedFacet(BoolFacet):
    def __init__(self, selection=None):
        super().__init__('', expression='row.flagged', selection=selection)


class BlankFacet(BoolFacet):
    def __init__(self, column, selection=None):
        super().__init__(column, expression='isBlank(value)', selection=selection)


class ReconJudgmentFacet(TextFacet):
    def __init__(self, column, **options):
        super().__init__(
            column,
            expression='forNonBlank(cell.recon.judgment, v, v, '
                       'if(isNonBlank(value), "(unreconciled)", "(blank)"))',
            **options,
        )


# Capitalize 'From' to get around python's reserved word.
class NumericFacet(Facet):
    def __init__(
            self, column,
            From=None, to=None,
            expression='value',
            select_blank=True,
            select_error=True,
            select_non_numeric=True,
            select_numeric=True,
            **options,
    ):
        super().__init__(
            column,
            facet_type='range',
            expression=expression,
            select_blank=select_blank,
            select_error=select_error,
            select_non_numeric=select_non_numeric,
            select_numeric=select_numeric,
            **options,
        )
        self.From = From
        self.to = to

    def reset(self):
        self.From = None
        self.to = None
        return self


class FacetResponse:
    """Class for unpacking an individual facet response."""

    def __init__(self, facet):
        self.name = None
        for k, v in facet.items():
            if isinstance(k, (bool, str)):
                setattr(self, from_camel(k), v)
        self.choices = {}

        class FacetChoice:
            def __init__(self, c):
                self.count = c['c']
                self.selected = c['s']

        if 'choices' in facet:
            for choice in facet['choices']:
                self.choices[choice['v']['v']] = FacetChoice(choice)
            if 'blankChoice' in facet:
                self.blank_choice = FacetChoice(facet['blankChoice'])
            else:
                self.blank_choice = None
        if 'bins' in facet:
            self.bins = facet['bins']
            self.base_bins = facet['baseBins']


class FacetsResponse:
    """FacetsResponse unpacking the compute-facets response.
    It has two attributes: facets & mode. Mode is either 'row-based' or
    'record-based'. facets is a list of facets produced by compute-facets, in
    the same order as they were specified in the Engine. By coupling the engine
    object with a custom container it's possible to look up the computed facet
    by the original facet's object.
    """

    def __init__(self, engine, facets):
        class FacetResponseContainer:
            facets = None

            def __init__(self, facet_responses):
                self.facets = [FacetResponse(fr) for fr in facet_responses]

            def __iter__(self):
                for facet in self.facets:
                    yield facet

            def __getitem__(self, index):
                if not isinstance(index, int):
                    index = engine.facet_index_by_id[id(index)]
                assert self.facets[index].name == engine.facets[index].name
                return self.facets[index]

        self.facets = FacetResponseContainer(facets['facets'])
        self.mode = facets['mode']


class Engine:
    """An Engine keeps track of Facets, and responses to facet computation."""

    def __init__(self, *facets, **kwargs):
        self.facets = []
        self.facet_index_by_id = {}  # dict of facets by Facet object id
        self.set_facets(*facets)
        self.mode = kwargs.get('mode', 'row-based')

    def set_facets(self, *facets):
        """facets may be a Facet or list of Facets."""
        self.remove_all()
        for facet in facets:
            self.add_facet(facet)

    def facets_response(self, response):
        """Unpack a compute-facets response."""
        return FacetsResponse(self, response)

    def __len__(self):
        return len(self.facets)

    def as_json(self):
        """Return a JSON string suitable for use as a POST parameter."""
        return json.dumps({
            'facets': [f.as_dict() for f in self.facets],  # XXX how with json?
            'mode': self.mode,
        })

    def add_facet(self, facet):
        # Record the facet's object id so facet response can be looked up by id
        self.facet_index_by_id[id(facet)] = len(self.facets)
        self.facets.append(facet)

    def remove_all(self):
        """Remove all facets."""
        self.facet_index_by_id = {}
        self.facets = []

    def reset_all(self):
        """Reset all facets."""
        for facet in self.facets:
            facet.reset()


class Sorting:
    """Class representing the current sorting order for a project.
    Used in RefineProject.get_rows()"""

    # noinspection PyTypeChecker
    def __init__(self, criteria=None):
        self.criteria = []
        if criteria is None:
            criteria = []
        if not isinstance(criteria, list):
            criteria = [criteria]
        for criterion in criteria:
            # A string criterion defaults to a string sort on that column
            if isinstance(criterion, str):
                criterion = {
                    'column': criterion,
                    'valueType': 'string',
                    'caseSensitive': False,
                }
            criterion.setdefault('reverse', False)
            criterion.setdefault('errorPosition', 1)
            criterion.setdefault('blankPosition', 2)
            self.criteria.append(criterion)

    def as_json(self):
        return json.dumps({'criteria': self.criteria})

    def __len__(self):
        return len(self.criteria)

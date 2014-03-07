from abc import ABCMeta, abstractmethod


class ServiceCollection(object):
    def __init__(self, services=None):
        self.services = services or []

    def __eq__(self, other):
        return self.services == other.services

    def render(self, r):
        """ Render this service collection out """
        for service in self.services:
            page = service.render_page(r)
            r.add_page(page)


class ServiceDescription(object):
    def __init__(self, name, module_path, class_name, sections=None):
        self.name = name
        self.module_path = module_path
        self.class_name = class_name
        self.sections = sections or []

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.module_path == other.module_path and
            self.class_name == other.class_name and
            self.sections == other.sections
        )

    def render_page(self, r):
        """ Render a service into a page """
        section_parts = [
            section.render_section(r, self, 2) for section in self.sections
        ]

        page = r.page(
            name=self.name,
            parts=[
                r.title(
                    text=self.name,
                    as_code=True,
                    level=1,
                ),
                r.include_module(
                    path=self.module_path,
                ),
            ] + section_parts,
        )
        return page


class BaseSection(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def render_section(self, r, service_description, this_level=1):
        """ Render a section out, providing the containing service, and the
        level the section is rendered at, for nested titles """


class ReferenceSection(BaseSection):
    def __init__(self, references=None):
        self.references = references or []

    def __eq__(self, other):
        return self.references == other.references

    def render_section(self, r, service_description, this_level=1):
        aside = r.see_also_section(
            contents=[
                r.definition_list(
                    contents=[
                        ref.render_reference(r)
                        for ref in self.references
                    ]
                )
            ]
        )
        return aside


class ClassReference(object):
    def __init__(self, title, reference_path):
        self.title = title
        self.reference_path = reference_path

    def __eq__(self, other):
        return (
            self.title == other.title and
            self.reference_path == other.reference_path
        )

    def render_reference(self, r):
        """ Render a reference to a class under a given category/title """
        return r.definition(
            term=self.title,
            description=r.class_reference(
                path=self.reference_path
            ),
        )


class Section(BaseSection):
    def __init__(self, title, contents=None):
        self.title = title
        self.contents = contents or []

    def __eq__(self, other):
        return (
            self.title == other.title and
            self.contents == other.contents
        )

    def render_section(self, r, service_description, this_level=1):
        sub_section_contents = [
            content.render_section(r, service_description, this_level + 1)
            for content in self.contents
        ]
        section = r.section(
            contents=[
                r.title(
                    text=self.title,
                    level=this_level,
                ),
            ] + sub_section_contents
        )
        return section


class SingleMethod(BaseSection):
    def __init__(self, method_name, extras=None):
        self.method_name = method_name
        self.extras = extras or []

    def __eq__(self, other):
        return (
            self.method_name == other.method_name and
            self.extras == other.extras
        )

    def render_section(self, r, service_description, this_level=1):
        method_path = '{}.{}.{}'.format(
            service_description.module_path,
            service_description.class_name,
            self.method_name
        )
        method_ref = r.include_method(
            path=method_path,
            no_index=True,
            extras=[
                extra.render_extra(r) for extra in self.extras
            ]
        )
        return method_ref


class ExtraInstruction(object):
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def render_extra(self, r):
        """ Render an extra instruction """
        return r.instruction(
            name=self.title,
            content=self.content
        )

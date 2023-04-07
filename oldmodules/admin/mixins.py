from wkhtmltopdf.views import PDFTemplateResponse, PDFTemplateView


class PDFTemplateViewMixin(PDFTemplateView):
    template_name = "print.html"
    # Send file as attachement. If True render content in the browser.
    show_content_in_browser = True

    def get_cover_template(self):
        return self.cover_template

    def get_header_template(self):
        return self.header_template

    def get_footer_template(self):
        return self.footer_template

    def get_template_names(self):
        return self.template_name

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a PDF response with a template rendered with the given context.
        """
        filename = response_kwargs.pop("filename", None)
        cmd_options = response_kwargs.pop("cmd_options", None)
        cover_template = response_kwargs.pop("cover_template", None)
        header_template = response_kwargs.pop("header_template", None)
        footer_template = response_kwargs.pop("footer_template", None)
        template_name = response_kwargs.pop("template_name", None)

        if issubclass(self.response_class, PDFTemplateResponse):

            if filename is None:
                filename = self.get_filename()

            if cmd_options is None:
                cmd_options = self.get_cmd_options()

            if cover_template is None:
                cover_template = self.get_cover_template()

            if header_template is None:
                header_template = self.get_header_template()

            if footer_template is None:
                footer_template = self.get_footer_template()

            if template_name is None:
                template_name = self.get_template_names()

            return super(PDFTemplateView, self).render_to_response(
                context=context,
                filename=filename,
                show_content_in_browser=self.show_content_in_browser,
                header_template=header_template,
                footer_template=footer_template,
                cmd_options=cmd_options,
                cover_template=cover_template,
                **response_kwargs
            )
        else:
            return super(PDFTemplateView, self).render_to_response(
                context=context, **response_kwargs
            )


class PDFPrintView(PDFTemplateViewMixin):
    pass

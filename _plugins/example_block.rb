# Worked-example asides: supporting material a reader can read or skip.
#
#   {% example A scheduling feature, sliced into six PRs %}
#   * PR 1 — ...
#   * PR 2 — ...
#   {% endexample %}
#
# The body is run through the site's markdown converter, so bullets, links,
# and inline formatting work as they do in the surrounding post.
#
# The label is a <div>, not a <p>, on purpose: _plugins/newsletter_inline.rb
# places the inline subscribe form by counting </p> tags in the body, and an
# example's label shouldn't shift that count.

module Jekyll
  class ExampleBlock < Liquid::Block
    def initialize(tag_name, markup, tokens)
      super
      @title = markup.strip
    end

    def render(context)
      converter = context.registers[:site]
                         .find_converter_instance(::Jekyll::Converters::Markdown)
      body = converter.convert(super.to_s)

      title_html = @title.empty? ? "" : " #{CGI.escapeHTML(@title)}"

      <<~HTML
        <aside class="example-block">
          <div class="example-block-label"><span class="example-block-kicker">Example:</span>#{title_html}</div>
          #{body}
        </aside>
      HTML
    end
  end
end

Liquid::Template.register_tag("example", Jekyll::ExampleBlock)

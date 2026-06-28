# Inject the inline newsletter subscribe form after the Nth paragraph of
# the post body, but only on posts long enough that a second form (the
# end-of-post one) won't crowd it.
#
# Counting starts at the .post-content div so <p> tags in the header
# (subtitle, post-meta date) don't shift the placement. We count from the
# opening tag forward rather than matching the whole div, because the body
# contains nested divs (code blocks, tables) that would break a naive
# open/close regex. The body-length count is bounded by </article> so the
# footer / end-of-post form paragraphs aren't included.

PARAGRAPH_INDEX = 2   # inject after this body paragraph
MIN_PARAGRAPHS = 5    # ...only if the post body has at least this many

Jekyll::Hooks.register :posts, :post_render do |post|
  next unless post.output

  include_path = File.join(post.site.source, "_includes", "subscribe-inline.html")
  next unless File.exist?(include_path)

  form_html = File.read(include_path)

  marker = post.output =~ /<div[^>]*class="[^"]*\bpost-content\b/
  next unless marker

  # Count only body paragraphs (post-content start up to </article>).
  article_end = post.output.index("</article>", marker) || post.output.length
  body_paragraphs = post.output[marker...article_end].scan(%r{</p>}i).length
  next if body_paragraphs < MIN_PARAGRAPHS

  head = post.output[0...marker]
  tail = post.output[marker..]

  para_count = 0
  tail = tail.gsub(%r{</p>}i) do |match|
    para_count += 1
    para_count == PARAGRAPH_INDEX ? "#{match}\n#{form_html}" : match
  end

  post.output = head + tail
end

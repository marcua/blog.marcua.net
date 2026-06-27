# Inject the inline newsletter subscribe form after the Nth paragraph of
# the post body. Counting starts at the .post-content div so <p> tags in
# the header (subtitle, post-meta date) don't shift the placement. We
# count from the opening tag forward (rather than matching the whole div)
# because the body contains nested divs (code blocks, tables) that would
# break a naive open/close regex.

PARAGRAPH_INDEX = 2

Jekyll::Hooks.register :posts, :post_render do |post|
  next unless post.output

  include_path = File.join(post.site.source, "_includes", "subscribe-inline.html")
  next unless File.exist?(include_path)

  form_html = File.read(include_path)

  marker = post.output =~ /<div[^>]*class="[^"]*\bpost-content\b/
  next unless marker

  head = post.output[0...marker]
  tail = post.output[marker..]

  para_count = 0
  tail = tail.gsub(%r{</p>}i) do |match|
    para_count += 1
    para_count == PARAGRAPH_INDEX ? "#{match}\n#{form_html}" : match
  end

  post.output = head + tail
end

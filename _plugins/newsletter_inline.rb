# Inject the inline newsletter subscribe form after the 3rd paragraph
# of each post. Only applies to the post layout, not pages/archives.

Jekyll::Hooks.register :posts, :post_render do |post|
  next unless post.output

  include_path = File.join(post.site.source, "_includes", "subscribe-inline.html")
  next unless File.exist?(include_path)

  form_html = File.read(include_path)
  para_count = 0

  post.output = post.output.gsub(%r{</p>}i) do |match|
    para_count += 1
    if para_count == 3
      "#{match}\n#{form_html}"
    else
      match
    end
  end
end

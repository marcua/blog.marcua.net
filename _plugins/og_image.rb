Jekyll::Hooks.register :posts, :pre_render do |post|
  next if post.data['image']

  slug = post.data['slug'] || File.basename(post.path, File.extname(post.path))
                                   .sub(/^\d{4}-\d{2}-\d{2}-/, '')
  og_path = "/assets/images/og/#{slug}.png"
  full_path = File.join(post.site.source, og_path)

  if File.exist?(full_path)
    post.data['image'] = og_path
  end
end

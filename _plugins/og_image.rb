Jekyll::Hooks.register :site, :after_init do |site|
  script = File.join(site.source, "_plugins", "generate_og_images.py")
  next unless File.exist?(script)

  Jekyll.logger.info "OG Images:", "Generating preview images..."
  output = `uv run #{script} 2>&1`
  status = $?
  if status.success?
    output.each_line { |l| Jekyll.logger.info "OG Images:", l.chomp }
  else
    output.each_line { |l| Jekyll.logger.warn "OG Images:", l.chomp }
  end
end

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

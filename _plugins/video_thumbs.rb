# Generate video thumbnails at build time (like OG images) and inject
# poster attributes into <video> tags so email clients can show a
# preview image.

Jekyll::Hooks.register :site, :after_init do |site|
  script = File.join(site.source, "_plugins", "generate_video_thumbs.py")
  next unless File.exist?(script)

  Jekyll.logger.info "Video Thumbs:", "Generating video thumbnails..."
  output = `uv run #{script} 2>&1`
  status = $?
  if status.success?
    output.each_line { |l| Jekyll.logger.info "Video Thumbs:", l.chomp }
  else
    output.each_line { |l| Jekyll.logger.warn "Video Thumbs:", l.chomp }
  end
end

# After rendering, inject poster= into any <video> tag that has a
# matching thumbnail on disk.
Jekyll::Hooks.register :posts, :post_render do |post|
  next unless post.output

  post.output = post.output.gsub(%r{<video([^>]*)>}i) do |match|
    attrs = $1
    next match if attrs.include?("poster")

    source_match = post.output[post.output.index(match)..].match(
      %r{<source[^>]+src=["'](/assets/video/([^"']+))["']}i
    )
    next match unless source_match

    video_rel = source_match[2]
    thumb_rel = video_rel.sub(/\.[^.]+$/, '.png')
    thumb_path = File.join(post.site.source, "assets", "images", "video-thumbs", thumb_rel)

    if File.exist?(thumb_path)
      poster_url = "/assets/images/video-thumbs/#{thumb_rel}"
      "<video#{attrs} poster=\"#{poster_url}\">"
    else
      match
    end
  end
end

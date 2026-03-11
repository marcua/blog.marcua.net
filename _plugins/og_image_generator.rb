require "open3"

module OgImageGenerator
  class Generator < Jekyll::Generator
    priority :highest

    def generate(site)
      script = File.join(site.source, "generate_og_images.py")
      unless File.exist?(script)
        Jekyll.logger.warn "OG Images:", "generate_og_images.py not found, skipping"
        return
      end

      Jekyll.logger.info "OG Images:", "Generating preview images..."
      stdout, stderr, status = Open3.capture3("python3", script, chdir: site.source)
      stdout.each_line { |line| Jekyll.logger.info "OG Images:", line.strip }

      unless status.success?
        Jekyll.logger.error "OG Images:", "generate_og_images.py failed:"
        stderr.each_line { |line| Jekyll.logger.error "OG Images:", line.strip }
      end
    end
  end
end

Jekyll::Hooks.register :posts, :pre_render do |post|
  if post.data['subtitle'] && !post.data['description']
    post.data['description'] = post.data['subtitle']
  end
end

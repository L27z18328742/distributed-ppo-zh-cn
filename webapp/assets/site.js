document.querySelectorAll('pre').forEach(pre => {
  const code = pre.querySelector('code');
  if (!code) return;
  const button = document.createElement('button');
  button.className = 'code-copy';
  button.type = 'button';
  button.textContent = '复制代码';
  button.setAttribute('aria-label', '复制此代码块');
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = '已复制';
      setTimeout(() => { button.textContent = '复制代码'; }, 1600);
    } catch {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = '已选中，请复制';
    }
  });
  pre.prepend(button);
});
const headings = document.querySelectorAll('.prose h2[id]');
if (headings.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      document.querySelectorAll('.toc a').forEach(a => {
        const active = a.getAttribute('href') === '#' + entry.target.id;
        a.classList.toggle('active', active);
        if (active) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-10% 0px -65% 0px' });
  headings.forEach(heading => observer.observe(heading));
}

document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (!navToggle || !navMenu) return;

  navToggle.addEventListener('click', () => {
    if (navMenu.style.display === 'flex') {
      navMenu.style.display = 'none';
    } else {
      const rect = navToggle.getBoundingClientRect();
      let leftPos = rect.left + window.scrollX;
      if (window.innerWidth <= 600) {
        if (leftPos + navMenu.offsetWidth > window.innerWidth - 10) {
          leftPos = window.innerWidth - navMenu.offsetWidth - 10;
        }
        if (leftPos < 10) leftPos = 10;
      }
      navMenu.style.top = (rect.bottom + window.scrollY) + 'px';
      navMenu.style.left = leftPos + 'px';
      navMenu.style.right = 'auto';
      navMenu.style.bottom = 'auto';
      navMenu.style.transform = 'none';
      navMenu.style.display = 'flex';
    }
  });

  document.addEventListener('click', (event) => {
    if (!navMenu.contains(event.target) && event.target !== navToggle) {
      navMenu.style.display = 'none';
    }
  });

  navToggle.style.position = 'fixed';
  navToggle.style.cursor = 'grab';

  let isDragging = false;
  let offsetX, offsetY;

  navToggle.addEventListener('mousedown', (e) => {
    isDragging = true;
    offsetX = e.clientX - navToggle.getBoundingClientRect().left;
    offsetY = e.clientY - navToggle.getBoundingClientRect().top;
    navToggle.style.cursor = 'grabbing';
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      let newLeft = e.clientX - offsetX;
      let newTop = e.clientY - offsetY;

      const maxLeft = window.innerWidth - navToggle.offsetWidth;
      const maxTop = window.innerHeight - navToggle.offsetHeight;
      if (newLeft < 0) newLeft = 0;
      if (newTop < 0) newTop = 0;
      if (newLeft > maxLeft) newLeft = maxLeft;
      if (newTop > maxTop) newTop = maxTop;

      navToggle.style.left = newLeft + 'px';
      navToggle.style.top = newTop + 'px';
      navToggle.style.right = 'auto';
      navToggle.style.bottom = 'auto';
    }
  });

  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      navToggle.style.cursor = 'grab';
    }
  });
});

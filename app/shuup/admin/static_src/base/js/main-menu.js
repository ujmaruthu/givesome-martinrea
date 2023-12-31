/**
 * This file is part of Shuup.
 *
 * Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
 *
 * This source code is licensed under the Shuup Commerce Inc -
 * SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
 * and the Licensee.
 */

const handleMainMenu = () => {
  const categoryLink = document.getElementsByClassName('item-category');

  const closeMenu = () => {
    Array.from(categoryLink).forEach((item) => {
      const categoryArrow = item.querySelector('.item-arrow');
      const submenu = item.nextElementSibling;

      if (item.classList.contains('item-active')) {
        item.classList.remove('item-active');
        submenu.classList.remove('active');
        categoryArrow.classList.remove('rotate');
      }
    });
  };

  const openMenu = (element) => {
    const categoryArrow = element.querySelector('.item-arrow');
    const submenu = element.nextElementSibling;

    element.classList.add('item-active');
    submenu.classList.add('active');
    categoryArrow.classList.add('rotate');
  };

  [...categoryLink].forEach((item) => {
    item.addEventListener('click', (event) => {
      event.preventDefault();

      const currentItem = event.currentTarget;
      const isActive = currentItem.classList.contains('item-active');

      closeMenu();
      openMenu(item);

      if (isActive) {
        closeMenu();
      }
    });
  });

  const toggleBtn = document.getElementById('menu-button');
  const mainMenu = document.getElementById('js-main-menu');
  const closeBtn = document.getElementById('js-menu-close');

  const hideMainMenu = () => {
    closeBtn.addEventListener('click', event => {
      event.preventDefault();
      mainMenu.classList.remove('open');
    });
  };

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      $("body").toggleClass("desktop-menu-closed");
      const menuOpen = ($("body").hasClass("desktop-menu-closed")) ? 0 : 1;
      $.post(window.ShuupAdminConfig.browserUrls.menu_toggle, { "csrfmiddlewaretoken": window.ShuupAdminConfig.csrf, menuOpen });
      if (mainMenu.classList.contains('open')) {
        mainMenu.classList.remove('open');
      } else {
        mainMenu.classList.add('open');
        hideMainMenu();
      }
    });
  }
};

handleMainMenu();
export default handleMainMenu;

const prevBtn = document.getElementById("prevBtn");
const pageSlider = document.getElementById("pageSlider");
const nextBtn = document.getElementById("nextBtn");
const galleryEl = document.getElementById("gallery");
const pageLabel = document.getElementById("pageLabel");
const dirTree = document.getElementById("directoryTree");

let selectedPath = null;
let selectedLi = null;

let gallery = new Object();
gallery.photos = []
gallery.photosPerPage = 30;
gallery.page = 1;
gallery.totalPages = 1;

async function fetchDirPhotos(path) {
  try {
    const res = await fetch(`/photos/list_dir/${encodeURIComponent(path)}`);
    photos = await res.json();
    renderGallery(photos);
  } catch (error) {
    console.error("Failed to load photos:", error);
    galleryEl.innerText = "Failed to load photos.";
  }
}

function renderGallery(photos) {
  try {
    gallery.photos = photos;
    gallery.totalPages = Math.ceil(gallery.photos.length / gallery.photosPerPage);
    pageSlider.max = gallery.totalPages;
    renderPage(1);
  } catch (error) {
    console.error("Failed to load photos:", error);
    galleryEl.innerText = "Failed to load photos.";
  }
}

function renderPage(page) {
  gallery.page = page;
  galleryEl.innerHTML = "";
  pageSlider.value = gallery.page;
  pageLabel.textContent = `Page ${gallery.page}`;

  const start = (gallery.page - 1) * gallery.photosPerPage;
  const end = start + gallery.photosPerPage;
  const pagePhotos = gallery.photos.slice(start, end);

  pagePhotos.forEach(path => {
    const img = document.createElement("img");
    img.src = `/photos/preview_small/${encodeURIComponent(path)}`;
    img.alt = path;
    galleryEl.appendChild(img);
  });

  prevBtn.disabled = (page === 1);
  nextBtn.disabled = (page === gallery.totalPages);
  console.info(page, gallery.totalPages, nextBtn.disabled)
}

function nextPage() {
  if (gallery.page < gallery.totalPages) {
    renderPage(gallery.page + 1);
  }
}

function prevPage() {
  if (gallery.page > 1) {
    renderPage(gallery.page - 1);
  }
}

pageSlider.addEventListener("input", () => {
  renderPage(Number(pageSlider.value));
});


async function fetchDirectoryStructure() {
  try {
    const res = await fetch("/photos/structure");
    const structure = await res.json();
    dirTree.innerHTML = "";
    console.info(res);
    console.info("STRUCTURE");
    console.info(structure)
    structure.forEach(node => {
      dirTree.appendChild(buildTree(node));
    });
  } catch (error) {
    console.error("Failed to load folder structure:", error);
    dirTree.innerText = "Failed to load folder structure.";
  }
}

function buildTree(node, parentPath = "") {
  const ul = document.createElement("ul");

  for (const key in node) {
    const li = document.createElement("li");
    const fullPath = parentPath ? `${parentPath}/${key}` : key;

    li.textContent = key;
    li.dataset.fullPath = fullPath;

    li.addEventListener("click", (event) => {
      event.stopPropagation(); // Prevent bubbling to parent folders
      if (selectedLi) selectedLi.classList.remove("selected");
      li.classList.add("selected");
      selectedLi = li;
      selectedPath = fullPath;
      console.log("Selected path:", selectedPath);
      fetchDirPhotos(selectedPath);
    });

    const children = node[key];
    if (children && children.length > 0) {
      children.forEach(child => {
        li.appendChild(buildTree(child, fullPath));
      });
    }
    ul.appendChild(li);
  }

  return ul;
}

fetchDirectoryStructure();
// fetchPhotos();

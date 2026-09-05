document.querySelectorAll(".table-search").forEach((input) => {
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    document.querySelectorAll(`#${input.dataset.target} tbody tr`).forEach((row) => {
      row.hidden = Boolean(query) && !row.textContent.toLowerCase().includes(query);
    });
  });
});
document.querySelectorAll(".stats article,.panel,.table-wrap,.form-card").forEach((el,index)=>{
  el.classList.add("fade-in");
  el.style.animationDelay=`${Math.min(index*60,300)}ms`;
});

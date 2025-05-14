document.addEventListener('DOMContentLoaded', () => {
    loadReviews();
  
    // 로그아웃
    document.getElementById('logoutBtn').onclick = () => location.href = '/logout';
  });
  
  // 전체 리뷰 불러오기
  function loadReviews() {
    fetch('/reviews-all')
      .then(res => res.json())
      .then(rows => {
        const tbody = document.querySelector('#reviewTable tbody');
        tbody.innerHTML = '';
        rows.forEach(r => {
          tbody.insertAdjacentHTML('beforeend', `
            <tr>
              <td>${r.id}</td>
              <td>
                <input value="${r.content}" data-id="${r.id}" />
              </td>
              <td>${r.created_at ?? ''}</td>
              <td>
                <button onclick="updateReview(${r.id})">수정</button>
                <button onclick="deleteReview(${r.id})">삭제</button>
              </td>
            </tr>
          `);
        });
      });
  }
  
  // 리뷰 수정
  function updateReview(id) {
    const newContent = document.querySelector(`input[data-id="${id}"]`).value;
    fetch(`/update-review/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ new_content: newContent })
    }).then(() => loadReviews());
  }
  
  // 리뷰 삭제
  function deleteReview(id) {
    fetch(`/delete-review/${id}`, { method: 'POST' })
      .then(() => loadReviews());
  }
  
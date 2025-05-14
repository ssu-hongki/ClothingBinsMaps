let map, searchMarker;

function initMap() {
  const gu = window.gu || "서울시";
  const centerGu = {
    '강남구': { lat: 37.5172, lng: 127.0473 },
    '서초구': { lat: 37.4837, lng: 127.0327 },
    '동작구': { lat: 37.5124, lng: 126.9390 },
    '관악구': { lat: 37.4784, lng: 126.9516 }
  };
  const defaultCenter = centerGu[gu] || { lat: 37.5665, lng: 126.9780 };

  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: defaultCenter
  });

  // 현재 위치 파란 원
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const userPos = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      map.setCenter(userPos);
      new google.maps.Circle({
        strokeColor: '#4285F4', strokeOpacity: 0.8, strokeWeight: 2,
        fillColor: '#4285F4', fillOpacity: 0.35, map,
        center: userPos, radius: 30
      });
    });
  }

  // 수거함 마커
  fetch(`/bins?gu=${gu}`)
    .then(r => r.json())
    .then(bins => {
      bins.forEach(bin => {
        const marker = new google.maps.Marker({
          position: { lat: bin.lat, lng: bin.lng },
          map, title: bin.name
        });
        marker.addListener('click', () => {
          document.getElementById('bin-title').textContent = bin.name;
          document.getElementById('bin-address').textContent = "주소: " + bin.address;
          document.getElementById('bin-id-input').value = bin.id;
          loadReviews(bin.id);
        });
      });
    });
}

function loadReviews(binId) {
  fetch(`/reviews?bin_id=${binId}`)
    .then(r => r.json())
    .then(rows => {
      const box = document.getElementById('reviews');
      box.innerHTML = "<h3>후기 목록</h3>";
      if (rows.length === 0) {
        box.innerHTML += "<p>작성된 후기가 없습니다.</p>";
        return;
      }
      rows.forEach(r => {
        let html = `<div><strong>🕒 ${r.created_at}</strong><br>${r.content}</div>`;
        if (isAdmin) {
          html += `
            <form method="POST" action="/delete-review/${r.id}">
              <button type="submit">삭제</button>
            </form>`;
        }
        box.innerHTML += "<hr>" + html;
      });
    });
}

function searchLocation() {
  const input = document.getElementById('search-input').value;
  const geocoder = new google.maps.Geocoder();
  geocoder.geocode({ address: input }, (results, status) => {
    if (status === 'OK') {
      const loc = results[0].geometry.location;
      map.setCenter(loc);
      if (searchMarker) searchMarker.setMap(null);
      searchMarker = new google.maps.Marker({
        position: loc, map,
        icon: { path: google.maps.SymbolPath.CIRCLE, scale: 8,
                fillColor: '#4285F4', fillOpacity: 1,
                strokeColor: '#fff', strokeWeight: 2 }
      });
    } else {
      alert('주소를 찾을 수 없습니다.');
    }
  });
}

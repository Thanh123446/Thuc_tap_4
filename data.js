// File: data.js
const du_lieu_nong_trai = {
  "type": "FeatureCollection",
  "features": [
    // --- THỬA ĐẤT 1 (Đa giác thực tế từ tọa độ bạn vẽ) ---
    {
      "type": "Feature",
      "properties": {
        "id": "T1",
        "ten": "Thửa 1",
        "cay_trong": "Lúa",
        "dien_tich": 2450,
        "do_am": 78,
        "nhiet_do": 30.5
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [105.9360464, 19.9730689],
            [105.9352425, 19.9732636],
            [105.9353906, 19.9738487],
            [105.9362644, 19.9736318],
            [105.9363448, 19.9733069],
            [105.9360464, 19.9730689]
          ]
        ]
      }
    },

    // --- THỬA ĐẤT 2 (Thửa đất liền kề) ---
    {
      "type": "Feature",
      "properties": {
        "id": "T2",
        "ten": "Thửa 2",
        "cay_trong": "Rau",
        "dien_tich": 1100,
        "do_am": 25, // Độ ẩm dưới 30% để test câu hỏi lọc cực trị / điều kiện
        "nhiet_do": 33.0
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [105.9363448, 19.9733069],
            [105.9362644, 19.9736318],
            [105.9371000, 19.9734500],
            [105.9370000, 19.9731000],
            [105.9363448, 19.9733069]
          ]
        ]
      }
    },

    // --- THỬA ĐẤT 3 (Thửa trồng Cây ăn quả) ---
    {
      "type": "Feature",
      "properties": {
        "id": "T3",
        "ten": "Thửa 3",
        "cay_trong": "Cây ăn quả",
        "dien_tich": 3200,
        "do_am": 62,
        "nhiet_do": 29.0
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [105.9352425, 19.9732636],
            [105.9344000, 19.9734000],
            [105.9345500, 19.9740000],
            [105.9353906, 19.9738487],
            [105.9352425, 19.9732636]
          ]
        ]
      }
    },

    // --- ĐIỂM MỐC 1: NHÀ KHO ---
    {
      "type": "Feature",
      "properties": {
        "id": "M1",
        "ten": "Nhà kho trung tâm",
        "loai": "nha_kho"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [105.9352425, 19.9730689]
      }
    },

    // --- ĐIỂM MỐC 2: GIẾNG NƯỚC ---
    {
      "type": "Feature",
      "properties": {
        "id": "M2",
        "ten": "Giếng tưới số 1",
        "loai": "gieng"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [105.9363448, 19.9738487]
      }
    }
  ]
};
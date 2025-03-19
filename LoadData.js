import React from 'react';

function LoadData({ instruments }) {
  // Выводим переданные данные для отладки
  console.log("LoadData: instruments prop:", instruments);

  // Если instruments — массив, используем его, иначе пытаемся получить массив из объекта
  const instrumentsArray = Array.isArray(instruments)
    ? instruments
    : (instruments ? Object.values(instruments) : []);

  // Выводим получившийся массив для отладки
  console.log("LoadData: instrumentsArray:", instrumentsArray);

  // Если данных нет или массив пустой, можно отобразить альтернативный UI
  if (!instrumentsArray || !instrumentsArray.length) {
    return <div>Нет данных по инструментам.</div>;
  }

  return (
    <div>
      {instrumentsArray.map((instrument, index) => (
        <div key={index}>
          {instrument.name || 'Без названия'}
        </div>
      ))}
    </div>
  );
}

export default LoadData; 
const issues = [
  {
    id: 1,
    description: '张三：电动车违停导致通行受阻',
    assignee: '张三',
    type: '功能问题',
    created: '2026-05-16 09:00',
    status: '延期修复',
  },
  {
    id: 2,
    description: '李四：登录按钮颜色与风格不一致',
    assignee: '李四',
    type: '体验问题',
    created: '2026-05-16 10:30',
    status: '正常',
  },
  {
    id: 3,
    description: '王五：表单验证未提示必要字段',
    assignee: '王五',
    type: '功能问题',
    created: '2026-05-16 11:20',
    status: '延期修复',
  },
  {
    id: 4,
    description: '赵六：页面滚动时卡顿体验差',
    assignee: '赵六',
    type: '体验问题',
    created: '2026-05-16 12:05',
    status: '正常',
  },
];

function createIssueTable() {
  const container = document.createElement('div');
  container.style.minHeight = '100vh';
  container.style.padding = '24px';
  container.style.background = '#f5f7fa';
  container.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

  const title = document.createElement('h1');
  title.textContent = '简约问题列表';
  title.style.margin = '0 0 16px 0';
  title.style.fontSize = '24px';
  title.style.color = '#0f172a';
  container.appendChild(title);

  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.borderCollapse = 'collapse';
  table.style.background = '#ffffff';
  table.style.boxShadow = '0 1px 4px rgba(15, 23, 42, 0.08)';

  const header = document.createElement('tr');
  ['问题描述', '跟进人', '问题类型', '录入时间', '问题状态'].forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    th.style.padding = '14px 16px';
    th.style.textAlign = 'left';
    th.style.fontWeight = '600';
    th.style.fontSize = '13px';
    th.style.color = '#334155';
    th.style.borderBottom = '1px solid #e2e8f0';
    header.appendChild(th);
  });
  table.appendChild(header);

  issues.forEach(issue => {
    const row = document.createElement('tr');
    row.style.borderBottom = '1px solid #e2e8f0';

    [
      issue.description,
      issue.assignee,
      issue.type,
      issue.created,
      issue.status,
    ].forEach((value, index) => {
      const td = document.createElement('td');
      td.textContent = value;
      td.style.padding = '14px 16px';
      td.style.fontSize = '14px';
      td.style.color = '#475569';
      if (index === 4) {
        td.style.fontWeight = '600';
        td.style.color = issue.status === '延期修复' ? '#b91c1c' : '#0f766e';
      }
      row.appendChild(td);
    });

    table.appendChild(row);
  });

  container.appendChild(table);
  return container;
}

window.addEventListener('DOMContentLoaded', () => {
  document.body.style.margin = '0';
  document.body.style.background = '#f5f7fa';
  document.body.appendChild(createIssueTable());
});

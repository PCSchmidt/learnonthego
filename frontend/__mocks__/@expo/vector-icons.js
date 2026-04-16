const React = require('react');

const MockIcon = (props) => React.createElement('Text', props, props.name || '');

module.exports = {
  Ionicons: MockIcon,
  MaterialIcons: MockIcon,
  FontAwesome: MockIcon,
  AntDesign: MockIcon,
};
